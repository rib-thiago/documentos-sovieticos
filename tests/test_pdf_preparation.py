"""Validação de receitas não permite opções arbitrárias ou transformação de eixos."""
import unittest
from backend.pdf_preparation import DEFAULT,image_recipe,bounded_pixels
from backend.editorial import EditorialError

class RecipeTests(unittest.TestCase):
    def test_recipe_does_not_accept_arbitrary_tools_or_rotation(self):
        self.assertEqual(image_recipe(DEFAULT),DEFAULT)
        for extra in ({'rotation':90},{'crop':'10x10'},{'command':'rm'}):
            with self.subTest(extra=extra),self.assertRaises(EditorialError):
                image_recipe({**DEFAULT,**extra})

    def test_limits_and_types_are_strict(self):
        for changed in ({'resize':'125%'},{'resize':1000},{'resize':True},{'erosion':2},{'threshold':True},{'threshold':256},{'grayscale':'yes'}):
            with self.subTest(changed=changed),self.assertRaises(EditorialError):
                image_recipe({**DEFAULT,**changed})

    def test_expanded_image_still_has_a_pixel_budget(self):
        bounded_pixels(612,792,300,{**DEFAULT,'resize':150})
        with self.assertRaises(ValueError):
            bounded_pixels(5000,6000,300,{**DEFAULT,'resize':150})
