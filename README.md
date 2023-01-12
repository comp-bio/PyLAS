# PyLAS.sh

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

Если у Вас уже есть извлечённый сигнал покрытия в формате .bcov, Вы можете запустить на нём подсчёт метрики так:

```bash
python3 pylas.py [файл в формате .bcov]
```

На выходе будет получен файл из 6 колонок:  
Хромосома, Координата начала, координата конца региона, Активная ширина спектра, Энтропия DTCWT, Зачение метрики LAS


## Содержимое репозитория

`data` — тестовые файлы для прогона локальной метрики LAS  
`results` — Результаты исследования поведения метрики и их комбинации в jupyter-ноутбуках  
`tools` — Инструменты генерации искусственного сигнала с аберрациями  
`pylas.py` — Подсчёт итоговой локальной метрики LAS средствами python3 из файлов bcov  
`pylas.sh` — Обёртка над `pylas.py`. На вход получает файл bam или cram, на выходе las-файл с метрикой
