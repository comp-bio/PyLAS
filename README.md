# SpECtоR — SEquence Cоverage Roughness

## PyLAS.sh

Скрипт подсчёта локальной метрики аберрации генома.

### Установка:

```bash
wget "https://raw.githubusercontent.com/comp-bio/PyLAS/main/pylas.sh" && chmod +x pylas.sh
```

### Использование:

```bash
./pylas.sh [cram или bam файл] [референсный геном для cram файла]
```

Референсный геном [GRCh38](http://ftp.ensembl.org/pub/current_fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.toplevel.fa.gz).


### Пример:

```bash
./pylas.sh ../CHM/NA19240.alt_bwamem_GRCh38DH.20150718.YRI.low_coverage.cram Homo_sapiens.GRCh38.dna.toplevel.fa
```

### Что происходит "под капотом"

1. Устанавливаются зависимости [mosdepth](https://github.com/brentp/mosdepth) и [bed2cov](https://github.com/comp-bio/Bed2Cov) для получения сигнала глубины покрытия генома в формате bcov.
2. Устанавливаются зависимости python3: PyWavelets, numpy
3. Скачивается скрипт pylas.py (.bcov -> .las)
4. Запускается извлечение значений покрытия (.bam -> .bed.gz -> .bcov) и осуществляется подсчёт метрики (.bcov -> .las)

## pylas.py

Основные преобразования сигнала происходят в файле `pylas.py`. 

```bash
pip3 install PyWavelets numpy
wget https://raw.githubusercontent.com/comp-bio/PyLAS/main/pylas.py
```

Если у Вас уже есть извлечённый сигнал покрытия в формате .bcov, Вы можете запустить на нём подсчёт метрики так:

```bash
python3 pylas.py [файл в формате .bcov]
```

На выходе будет получен файл из 6 колонок:  
Хромосома, Координата начала, координата конца региона, Активная ширина спектра, Энтропия DTCWT, Зачение метрики LAS


## О проекте

Сохранение целостности генома - залог нормального функционирования организма и передачи наследственных признаков в ряду 
поколений. Некоторые участки генома менее стабильны и более подвержены повреждениям, что, возможно, связано с 
эволюционной избирательностью механизмов поддержания целостности генома. Накопление нарушений и повреждений в геноме 
является характерным признаком различных болезней, таких, как нейропсихиатрические расстройства и рак.

## Цель

Важным шагом на пути к пониманию работы механизмов, обеспечивающих поддержание стабильности генома, является создание 
методов количественной оценки его целостности. Метрики, характеризующие стабильность, помогут понять то, как связаны 
геномная архитектура, механизмы поддержания целостности генома и фенотипические признаки. Например, при изучении 
онкологических трансформаций, они смогут обрисовать сложные геномные перестройки и процессы, негативно влияющие на 
генетический (геномный) гомеостаз.

Получение интегральных характеристик сложных фенотипических признаков, связанных со стабильностью генома, послужит 
стимулом для разработки клинических биомаркеров, которые могут быть использованы для выбора новых стратегий лечения.

## Содержимое репозитория

`data` — тестовые файлы для прогона локальной метрики LAS  
`results` — Результаты исследования поведения метрики и их комбинации в jupyter-ноутбуках  
`tools` — Инструменты генерации искусственного сигнала с аберрациями  
`pylas.py` — Подсчёт итоговой локальной метрики LAS средствами python3 из файлов bcov  
`pylas.sh` — Обёртка над `pylas.py`. На вход получает файл bam или cram, на выходе las-файл с метрикой


### PYGENOMICS

Программный пакет, реализующий чтение, запись и преобразование геномных интервалов между различными форматами файлов 
данных, использующихся в геномной биоинформатике. Процедуры пакета могут быть легко включены в конвейерные системы 
обработки данных, таких как, например, Snakemake.

[Репозиторий](https://gitlab.com/gtamazian/pygenomics).  
[Дополнительный пакет](https://gitlab.com/gtamazian/pygenomics-ext). 
[Примеры использования](https://gitlab.com/gtamazian/pygenomics-examples).

### РЕПОЗИТОРИЙ СТРУКТУРНЫХ ВАРИАНТОВ
Вычислительный ресурс, содержащий аннотированные паттерны сигналов покрытия последовательности, а также модели профилей сигналов, соответствующие пяти основным типам структурных вариаций. База данных содержит около 23 миллионов профилей сигналов покрытия, извлеченных из данных полногеномного секвенирования, предоставленных несколькими крупномасштабными геномными проектами (например, HGDP). Инструменты работы с данными позволяют проводить поиск и визуализацию имеющихся данных, а также выгружать профили сигналов для дальнейшей работы.

[SWaveform](https://swaveform.compbio.ru/)


## Данные

Список элементов генома, подверженных аберрациям при онкозаболеваниях.  
https://spector.dobzhanskycenter.org/data/2021/GEL_FF_Genomic_regions/

## Результаты

В результате исследований были получены следующие значимые результаты:

* Создана база данных открытого доступа, содержащая каталог устойчивых форм сигнала покрытия, соответствующих структурным вариантам различных типов. Ресурс содержит более 23 млн. профилей.
* Построены марковские модели профилей сигналов покрытия, соответствующих различным типам структурных вариантов.
* В результате статистического анализа были идентифицированы экспериментальные факторы, вносящие наиболее значимый вклад в аберрации сигналов покрытия, а также охарактеризованы геномные элементы, способствующие нарушениям целостности генома в норме и патологии.
* Получен список участков генома, подверженных перестройкам и связанных с утратой целостности при различных онкозаболеваниях.
* Для расчета глобальной метрики нестабильности на основе геномов здоровой популяции создан эталонный набор данных значений меры локальной аберрации (local aberration score), позволяющий оценивать целостность отдельных геномов и сравнивать их между собой.
* Согласно результатам тестирования выбрана оптимальная методика вычисления показателя локальной аберрантности сигнала покрытия.
* Разработана новая статистическая модель обнаружения ранее нерегистрируемых событий (novelty detection) в сигнале покрытия.
* Представлена радикально переработанная версия программного пакета (бета‒версия аналитической среды) вычисления локальной меры аберрантности покрытия и глобальной метрики целостности генома.
* Разработан новый пакет Pygenomics для работы с интервальными данными.
* По результатам исследований опубликована одна статья (Q1) и один препринт (arXiv.org). Готовятся к публикации три статьи. Также результаты были представлены на трех международных конференциях в Корее, США и России.

## Схема построения обобщённой метрики:

1. Из первых 4 образцов GIAB выбираются реальные регионы, с однозначно хорошим сигналом покрытия: полностью покрытые, 
пересечение с `all_diff` < 5%. Для них строится распределение метрики `FFT_dF`. Для этих регионов извлекаются 
константы нормировки метрики для сведения итогового распределения `FFT_dF` к `Std` == 1 и приведения 95% квантилю к `10`.

Число `10` здесь выбрано произвольно, может быть любым. Это число — порог итоговой объединённой метрики. 
Все регионы, значения итоговой метрики для которых меньше порога, будут считаться спокойными, больше — аберрантными.

```text
FFT Std:  289.49012689247957
FFT Q95:  3510.6100249999977
```

Таким образом, при нормировке `FFT` на `Std` мы получим распределение, 95% квантиль которого будет расположен в 
точке=`10`, а значение в ненормированных данных для этого же значения будет равно `3510.6100249999977`.

2. Метрика делится на "грубую" `FFT_dF`, чувствительную к большим возмущениям, и "тонкую" `DTCWT_Entropy`, 
которая может заметить аберрации даже в одну базу. Первой применяется грубая метрика `FFT_dF`. Если её значения 
для анализируемого региона лежат за пределами 95% квантиля распределения образцовых очень хороших данных, то мы 
считаем, что регион содержит достаточно аберраций, чтобы они были замечены `FFT_dF`. В этом случае возвращаем 
значение `FFT_dF` нормированное таким образом, чтобы 95% приходился на 10. Следовательно, все значения `FFT_dF` 
всегда окажутся больше 10.


3. В противном же случае, если значения для метрики `FFT_dF` принадлежат 95% квантилю распределения образцовых очень 
хороших регионов, мы считаем, что аберрации в этих регионах настолько малы, что не могут быть замечены 
метрикой `FFT_dF`. На таких образцах считается метрика `DTCWT_Entropy`. Чем больше значения этой метрики, тем более 
спокойный регион в рассмотрении. По этому значения `DTCWT_Entropy` инвертируются и приводятся к интервалу от 0 до 10 
таким образом, чтобы распределение для всех хороших (в смысле `FFT_dF`) регионов было **равномерным**.

Для этого строится специальная функция, приводящая распределение образцовых очень хороших регионов (из первых 4 
образцов GIAB) к равномерному распределению 0 до 10. Если область определения этой функции — все значения
`DTCWT_Entropy`, то область значений — интервал [0, 10]. Функция определена как значения в узловых точках 
(100 точке, `dtt_grid` в коде) — для промежуточных значений (вне узлов) используется линейная интерполяция. 
