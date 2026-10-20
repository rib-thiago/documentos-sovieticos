# Conversão do espelho Perpetrator2004

Atualização da análise posterior: foram encontrados marcadores de notas sem conteúdo em 19 extrações. Consulte o [parecer e as pendências](../comparacao-perpetrator-showtrials/PARECER.md) antes de importar.

Foram encontrados 95 arquivos `.doc`: 95 convertidos, 0 falhas e 23 conversões com alertas estruturais.

Originais preservados em `temporario/showtrials-portatil-20261015-003451/showtrials-portatil-20261015-003451/referencia-projeto/data/perpetrator2004/raw/mirror`.
Markdown: `temporario/perpetrator2004-markdown/markdown/`; extrações intermediárias: `temporario/perpetrator2004-markdown/docbook/`.

## Limites e conferência manual

Conversão por antiword 0.37 → DocBook XML → Markdown (markdownify). Os arquivos Word não foram alterados. A divisão em pastas foi mantida, inclusive os documentos já extraídos de arquivos compactados. Nenhum documento foi cadastrado no site nesta entrega.

A conversão não certifica fidelidade integral. Compare o início, o fim e as notas com o Word; nos cinco arquivos com tabelas, confira também as células e a ordem de leitura. Imagens, objetos incorporados, paginação, comentários e controle de alterações do Word não têm preservação garantida por este método. Os alertas indicam estruturas detectadas, não uma revisão humana completa. Títulos internos não foram inferidos a partir do conteúdo.

Propriedades do Word (autor do arquivo, data de edição e título de aplicativo) ficam preservadas no XML, sem serem confundidas com os metadados históricos do documento. Erros de grafia ou de codificação herdados não foram corrigidos silenciosamente.

O CSV permite filtrar `status`, `avisos` e `erro`. O JSON inclui hashes dos originais e dos Markdown, diagnósticos do conversor, contagens de notas e trechos inicial e final.

## Falhas

Nenhum arquivo deixou de gerar Markdown.

## Arquivos e pendências

| Arquivo convertido | Resultado | Conferência prioritária |
| --- | --- | --- |
| [Bukharin_Confrontations.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Bukharin/Bukharin_Confrontations.md) | convertido | Conferência geral com o Word. |
| [Bukharin_Letter_April15_1937.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Bukharin/Bukharin_Letter_April15_1937.md) | convertido | Conferência geral com o Word. |
| [Bukharin_Letters.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Bukharin/Bukharin_Letters.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Plea_For_Pardon.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Bukharin/Plea_For_Pardon.md) | convertido | Conferência geral com o Word. |
| [Serovs_Letter_re_Bukharin_Trial.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Bukharin/Serovs_Letter_re_Bukharin_Trial.md) | convertido | Conferência geral com o Word. |
| [To_Future_Generation_of_Party_Leaders.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Bukharin/To_Future_Generation_of_Party_Leaders.md) | convertido | Conferência geral com o Word. |
| [StalinDocsDP.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/DoctorsPlot/StalinDocsDP.md) | convertido | Conferência geral com o Word. |
| [Beria_Order_00689.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Beria_Order_00689.md) | convertido | Conferência geral com o Word. |
| [CEC_Order_dated_1_12_1934.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/CEC_Order_dated_1_12_1934.md) | convertido | Conferência geral com o Word. |
| [Circular_Letter_106_20_May_1938.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Circular_Letter_106_20_May_1938.md) | convertido | Conferência geral com o Word. |
| [Coded_Telegram_On_Physical_Influence.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Coded_Telegram_On_Physical_Influence.md) | convertido | Conferência geral com o Word. |
| [Lead_Up_To_Terror.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Lead_Up_To_Terror.md) | convertido | Conferência geral com o Word. |
| [Letter_On_POV.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Letter_On_POV.md) | convertido | Conferência geral com o Word. |
| [Number_of_Arrested_Condemned_by_Organs.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Number_of_Arrested_Condemned_by_Organs.md) | convertido_com_alertas | Conferir tabelas, células mescladas e sequência de leitura no Word. |
| [Number_of_Condemned_by_Special_Commission.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Number_of_Condemned_by_Special_Commission.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Operative_Order_00439.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Operative_Order_00439.md) | convertido | Conferência geral com o Word. |
| [Operative_Order_00447.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Operative_Order_00447.md) | convertido_com_alertas | Conferir tabelas, células mescladas e sequência de leitura no Word. |
| [Operative_Order_00485.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Operative_Order_00485.md) | convertido | Conferência geral com o Word. |
| [Operative_Order_00486.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Operative_Order_00486.md) | convertido | Conferência geral com o Word. |
| [Operative_Order_00593.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Operative_Order_00593.md) | convertido | Conferência geral com o Word. |
| [Politburo_Resolution_5_7_37.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Politburo_Resolution_5_7_37.md) | convertido | Conferência geral com o Word. |
| [Pospelov_Commission_Report.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Pospelov_Commission_Report.md) | convertido_com_alertas | Conferir tabelas, células mescladas e sequência de leitura no Word. |
| [Shvernik_Report.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Great_Terror/Shvernik_Report/Shvernik_Report.md) | convertido_com_alertas | Conferir tabelas, células mescladas e sequência de leitura no Word.; Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Khrushchev13May1957.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Khrushchev/Khrushchev13May1957.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Khrushchev19May1957.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Khrushchev/Khrushchev19May1957.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Maniege1962.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Khrushchev/Maniege1962.md) | convertido | Conferência geral com o Word. |
| [Meeting_with_Intelligentsia.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Khrushchev/Meeting_with_Intelligentsia.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Speech16March1948.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Khrushchev/Speech16March1948.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Speech3WritCongr.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Khrushchev/Speech3WritCongr.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Kremlin_Affair_1.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_1.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_10.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_10.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_11.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_11.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_12.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_12.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_13.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_13.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_14.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_14.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_15.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_15.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_16.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_16.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_17.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_17.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_18.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_18.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_19.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_19.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_2.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_2.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_3.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_3.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_4.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_4.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_5.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_5.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_6.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_6.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_7.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_7.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_8.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_8.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_9.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_9.md) | convertido | Conferência geral com o Word. |
| [Kremlin_Affair_Memorandum.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Kremlin_Affair/Kremlin_Affair_Memorandum.md) | convertido | Conferência geral com o Word. |
| [Church_Values_Confiscation.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Lenin/Church_Values_Confiscation.md) | convertido | Conferência geral com o Word. |
| [Letter_to_the_Congress.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Lenin/Letter_to_the_Congress.md) | convertido | Conferência geral com o Word. |
| [Khrushchev_Speech_Leningrad.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Leningrad_Affair/Khrushchev_Speech_Leningrad.md) | convertido | Conferência geral com o Word. |
| [Rudenko_Speech_Leningrad.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Leningrad_Affair/Rudenko_Speech_Leningrad.md) | convertido | Conferência geral com o Word. |
| [Bukharin_Trial.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Show_Trials/Bukharin_Trial.md) | convertido | Conferência geral com o Word. |
| [CPSU_Classified_Letter_on_Trotskyite_Zinovievite_Bloc.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Show_Trials/CPSU_Classified_Letter_on_Trotskyite_Zinovievite_Bloc.md) | convertido | Conferência geral com o Word. |
| [Orlov_Prison_Shooting.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Show_Trials/Orlov_Prison_Shooting.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Radek_Pyatakov_Trial.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Show_Trials/Radek_Pyatakov_Trial.md) | convertido_com_alertas | Conferir tabelas, células mescladas e sequência de leitura no Word. |
| [Radek_Sokolnikov_Murder.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Show_Trials/Radek_Sokolnikov_Murder.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Zinoviev_Kamenev_Trial.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Show_Trials/Zinoviev_Kamenev_Trial.md) | convertido | Conferência geral com o Word. |
| [Plan_for_Defeat.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Tukhachevsky/Plan_for_Defeat.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Доклад комиссии по Тухачевскому.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Tukhachevsky/Tukhachevsky_Report/%D0%94%D0%BE%D0%BA%D0%BB%D0%B0%D0%B4%20%D0%BA%D0%BE%D0%BC%D0%B8%D1%81%D1%81%D0%B8%D0%B8%20%D0%BF%D0%BE%20%D0%A2%D1%83%D1%85%D0%B0%D1%87%D0%B5%D0%B2%D1%81%D0%BA%D0%BE%D0%BC%D1%83.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Kirshon_s_Report_on_Yagoda_s_Behavior_in_Prison.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Yagoda/Kirshon_s_Report_on_Yagoda_s_Behavior_in_Prison.md) | convertido | Conferência geral com o Word. |
| [Prosecutors_Interrogation_Record.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Yagoda/Prosecutors_Interrogation_Record.md) | convertido | Conferência geral com o Word. |
| [Shothand_Record_of_Closed_Session.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Yagoda/Shothand_Record_of_Closed_Session.md) | convertido | Conferência geral com o Word. |
| [Yagoda_Confrontation_Records.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Yagoda/Yagoda_Confrontation_Records.md) | convertido | Conferência geral com o Word. |
| [Yagoda_Interrogation_Records.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Yagoda/Yagoda_Interrogation_Records.md) | convertido | Conferência geral com o Word. |
| [Yagoda_Search_Record.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Yagoda/Yagoda_Search_Record.md) | convertido | Conferência geral com o Word. |
| [Yezhov1.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Yezhov/Yezhov1.md) | convertido | Conferência geral com o Word. |
| [Yezhov2.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Yezhov/Yezhov2.md) | convertido | Conferência geral com o Word. |
| [YezhovQuiz26Apr1939.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/Yezhov/YezhovQuiz26Apr1939.md) | convertido | Conferência geral com o Word. |
| [CCC_Memo_Shatunovskaya.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/CCC_Memo_Shatunovskaya.md) | convertido | Conferência geral com o Word. |
| [Draft_Circular_Letter.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Draft_Circular_Letter.md) | convertido | Conferência geral com o Word. |
| [Khanik_Documents_Records.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Khanik_Documents_Records.md) | convertido | Conferência geral com o Word. |
| [Kirilina_Interview.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Kirilina_Interview.md) | convertido | Conferência geral com o Word. |
| [Kotolynov_Interrogation_Record.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Kotolynov_Interrogation_Record.md) | convertido | Conferência geral com o Word. |
| [Kotolynov_Interrogation_Record_12_Dec.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Kotolynov_Interrogation_Record_12_Dec.md) | convertido | Conferência geral com o Word. |
| [Kotolynov_s_Statement_re_Indictment.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Kotolynov_s_Statement_re_Indictment.md) | convertido | Conferência geral com o Word. |
| [Kozlov_Memo.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Kozlov_Memo.md) | convertido | Conferência geral com o Word. |
| [Krov_Assassination_Memo_GPO_KGB.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Krov_Assassination_Memo_GPO_KGB.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Molotov_Commission_Borisov.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Molotov_Commission_Borisov.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Molotov_Commission_Memo.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Molotov_Commission_Memo.md) | convertido | Conferência geral com o Word. |
| [Nikolayev_Interrogation_Record_13_Dec.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Nikolayev_Interrogation_Record_13_Dec.md) | convertido | Conferência geral com o Word. |
| [Professor_Dembo_s_Letter.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Professor_Dembo_s_Letter.md) | convertido | Conferência geral com o Word. |
| [Record_No_2.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Record_No_2.md) | convertido | Conferência geral com o Word. |
| [Roslakov1.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Roslakov1.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Salkov_Statement.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Salkov_Statement.md) | convertido | Conferência geral com o Word. |
| [Serov_Memo_Volkova.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Serov_Memo_Volkova.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Shatunovskaya_Letters.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Shatunovskaya_Letters.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Special_Reports_to_Yagoda.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Special_Reports_to_Yagoda.md) | convertido | Conferência geral com o Word. |
| [TheUnknownKirov.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/TheUnknownKirov.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Trial_Record_Khanik.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Trial_Record_Khanik.md) | convertido | Conferência geral com o Word. |
| [Trial_Record_Kotolynov_et_al.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Trial_Record_Kotolynov_et_al.md) | convertido | Conferência geral com o Word. |
| [Volkova_s_Letter_Verification.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Volkova_s_Letter_Verification.md) | convertido_com_alertas | Conferir notas e referências: convertidas as notas identificadas no DocBook. |
| [Yakovlev_Memo.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Yakovlev_Memo.md) | convertido | Conferência geral com o Word. |
| [Zhukov_on_Kirov.doc](../../../temporario/perpetrator2004-markdown/markdown/documents/kirov/Zhukov_on_Kirov.md) | convertido | Conferência geral com o Word. |
