"""Receitas limitadas de imagem, sem substituir PDF, extração ou revisões."""
from __future__ import annotations
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import tempfile
from .editorial import EditorialError

DEFAULT = {'grayscale': True, 'contrast': False, 'threshold': None, 'resize': 100, 'erosion': 0}

def image_capabilities():
    engine=shutil.which('magick') or shutil.which('convert')
    return {'available': bool(engine and shutil.which('pdftoppm')), 'engine': engine,
            'operations': ['grayscale','contrast','threshold','resize','erosion'],
            'note': 'Sem recorte ou rotação: coordenadas normalizadas mantêm os eixos da página.'}

def image_engine_version():
    engine=image_capabilities()['engine']
    if not engine:return None
    try:return subprocess.run([engine,'-version'],check=True,capture_output=True,text=True,timeout=8).stdout.splitlines()[0]
    except (OSError,subprocess.SubprocessError,IndexError):return engine

def image_recipe(value):
    if not isinstance(value,dict) or set(value)!=set(DEFAULT):
        raise EditorialError('Receita de imagem inválida')
    if any(type(value[k]) is not bool for k in ('grayscale','contrast')):
        raise EditorialError('Opções de imagem inválidas')
    if value['threshold'] is not None and (type(value['threshold']) is not int or not 0<=value['threshold']<=255):
        raise EditorialError('Use limiar entre 0 e 255')
    if type(value['resize']) is not int or value['resize'] not in (50,75,100,125,150) or type(value['erosion']) is not int or value['erosion'] not in (0,1):
        raise EditorialError('Escala ou erosão de imagem inválida')
    return dict(value)

def apply_image(source, destination, recipe):
    recipe=image_recipe(recipe);engine=image_capabilities()['engine']
    if not engine:raise ValueError('ImageMagick indisponível para esta receita')
    command=[engine,'-limit','memory','256MiB','-limit','map','512MiB',str(source)]
    if recipe['grayscale']:command+=['-colorspace','Gray']
    if recipe['contrast']:command+=['-normalize']
    if recipe['threshold'] is not None:command+=['-threshold',f"{recipe['threshold']/255*100:.6f}%"]
    if recipe['resize']!=100:command+=['-resize',str(recipe['resize'])+'%']
    if recipe['erosion']:command+=['-morphology','Erode','Diamond:1']
    command+=['-strip',str(destination)]
    subprocess.run(command,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=60,env={**os.environ,'MAGICK_THREAD_LIMIT':'1'})

def bounded_pixels(width,height,dpi,recipe=None):
    scale=(recipe or {}).get('resize',100)/100
    w,h=float(width)*dpi/72*scale,float(height)*dpi/72*scale
    if max(w,h)>10000 or w*h>40000000:raise ValueError('Página ou derivado excede o limite de imagem; reduza DPI ou escala.')

class PDFPreparation:
    def __init__(self,sources):
        self.sources=sources;self.directory=sources.directory/'image-derivatives';self.directory.mkdir(exist_ok=True)
    def artifact(self,image_id,suffix='.png'):
        if not isinstance(image_id,str) or not re.fullmatch(r'img-[a-f0-9]{64}',image_id):raise EditorialError('Derivado não encontrado',404)
        path=self.directory/(image_id+suffix)
        if not path.is_file() or path.is_symlink():raise EditorialError('Derivado não encontrado',404)
        return path
    def preview(self,payload):
        if not isinstance(payload,dict) or set(payload)!={'source_id','page_number','dpi','recipe'}:raise EditorialError('Prévia de imagem inválida')
        source=self.sources.source(payload['source_id']);number=payload['page_number'];dpi=payload['dpi'];recipe=image_recipe(payload['recipe'])
        if type(number) is not int or not 1<=number<=(source['page_count'] or 0):raise EditorialError('Aguarde o inventário e escolha uma página válida')
        if type(dpi) is not int or dpi not in (150,200,300):raise EditorialError('Use 150, 200 ou 300 DPI')
        if not image_capabilities()['available']:raise EditorialError('Prévia exige Poppler e ImageMagick instalados',409)
        identity={'version':'image-v1','image_engine':image_engine_version(),'source_id':source['id'],'source_sha256':source['sha256'],'page_number':number,'dpi':dpi,'recipe':recipe}
        image_id='img-'+hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        with (self.directory/(image_id+'.lock')).open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            png=self.directory/(image_id+'.png');metadata=self.directory/(image_id+'.json')
            if not png.exists():
                metadata.write_text(json.dumps(identity),encoding='utf-8')
                try:subprocess.run([sys.executable,'-m','backend.pdf_preparation',str(self.sources.root),image_id],cwd=Path(__file__).resolve().parents[1],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=100)
                except (OSError,subprocess.SubprocessError) as error:raise EditorialError('Não foi possível preparar esta imagem. Reduza DPI/escala ou confira ImageMagick e Poppler.',409) from error
            with png.open('rb') as handle:digest=hashlib.file_digest(handle,'sha256').hexdigest()
            result={**identity,'image_id':image_id,'derivative_sha256':digest,'url':'/api/editorial/pdf/image/'+image_id+'/image.png'}
            metadata.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
        return result

def render_preview(root,image_id):
    if not re.fullmatch(r'img-[a-f0-9]{64}',image_id):raise SystemExit(2)
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));resource.setrlimit(resource.RLIMIT_CPU,(90,90));resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,64*1024**2))
    directory=Path(root)/'.local/research/image-derivatives';data=json.loads((directory/(image_id+'.json')).read_text());source_id=data['source_id']
    if not re.fullmatch(r'pdf-[a-f0-9]{32}',source_id):raise SystemExit(2)
    source=Path(root)/'.local/research/sources'/(source_id+'.pdf')
    with source.open('rb') as handle:
        if hashlib.file_digest(handle,'sha256').hexdigest()!=data['source_sha256']:raise SystemExit(3)
    from pypdf import PdfReader
    page=PdfReader(source).pages[data['page_number']-1];bounded_pixels(page.mediabox.width,page.mediabox.height,data['dpi'],data['recipe'])
    with tempfile.TemporaryDirectory(dir=directory,prefix='image-') as temporary:
        prefix=str(Path(temporary)/'page')
        subprocess.run(['pdftoppm','-f',str(data['page_number']),'-l',str(data['page_number']),'-singlefile','-r',str(data['dpi']),'-png',str(source),prefix],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=60)
        target=Path(temporary)/'processed.png';apply_image(prefix+'.png',target,data['recipe']);os.replace(target,directory/(image_id+'.png'))

if __name__=='__main__':render_preview(*sys.argv[1:])
