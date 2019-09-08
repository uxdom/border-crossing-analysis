# Border Crossing Analyzer
A small Python program that calculates monthly totals and running averages of vehicles, equipment, passengers and pedestrians crossing into the United States by land.

## Table of Contents
1. [Motivation](README.md#motivation)
2. [Features](README.md#features)
3. [Functions](README.md#functions)
4. [Instructions](README.md#instructions)
5. [Notes](README.md#notes)
6. [License](README.md#license)


## Motivation
The Bureau of Transportation Statistics regularly makes available data [here](https://data.transportation.gov/Research-and-Statistics/Border-Crossing-Entry-Data/keg4-3bc2) on the number of vehicles, equipment, passengers and pedestrians crossing into the United States by land. Currently there is no feature on their data visualization platform to calculate monthly running averages per crossing type. 

## Features
This program calculates monthly total for crossing type and attaches running averages next to the result in a single `output.csv` file. While there are 12 types of crossings in a given dataset for now, this may increase, decrease or change. This program is agnostic for any type of crossing it encounters in a given dataset. While it will correct upper case and lower case typos, it will also create a new crossing type if they exist. Solution also works for any given column order as long as columns are named as `Border`, `Data`, `Measure` and `Value`. Additionally dates contain days of the month, they are ignored and any date of the month is assigned to that month.

## Functions
There are five functions being used in this program. All designed modular and can be used standalone for your needs.

### CSV Loader (Helper Function)
This function takes in `source` csv file and strips `columns` that has been passed as array of strings such as `['Column 1', 'Column 2', ... ]` needs to include all four `[ 'Border', 'Data', 'Measure', 'Value' ]` in order.
```
def csv_to_dict_loader(source, columns):
    records = []
    with open(SOURCE_CSV, mode = "r") as file:
        csv_reader = csv.DictReader(file)
        line_count = 0
        for row in csv_reader:
            record = []
            date_pattern = re.search(r'([0-9]{1,2})[-/:]([0-9]{1,2})[-/:]([0-9]{4})', row['Date'])
            if len(str(date_pattern.group(1))) == 2:
                standardate  = date_pattern.group(1)+'/'+'01'+'/'+date_pattern.group(3)+' 12:00:00 AM'
            else:
                standardate  = '0'+date_pattern.group(1)+'/'+'01'+'/'+date_pattern.group(3)+' 12:00:00 AM'            
            standardate  = date_pattern.group(1)+'/'+'01'+'/'+date_pattern.group(3)+' 12:00:00 AM'
            row['Date'] = standardate
            for col in columns:
                try:
                    record.append(row[col.title()])
                except KeyError:
                    pass
            records.append(record)
            line_count += 1
        file.close()
    return sorted(records, key=lambda x: datetime.strptime(x[1], '%m/%d/%Y %I:%M:%S %p' ), reverse=True)

```

### Unique Value Counter (Helper Function)
A helper snippet that counts list elements with values and returns a dictionary of unique `{Measure 1 : int(Total Value) , Measure 2 : int(Total Value), ... }` 
```
def unique_value_counter(list):
    sums = {}
    for means, val in dict:
        means = means.title()
        if means in sums:
            sums[means] += int(val)
        else:
            sums[means] = int(val)
    if sums:
        return sums
```

### Month Year Iterator (Helper Function)
This function iterates over starting month, year - ending month, year by returning tuples `(year, month)`. 
>Ending Month is not included so you need to add `end_month + 1` to include ending month in your analysis
```
def month_year_iterator(start_month, start_year, end_month, end_year):
    ym_start= 12*start_year + start_month - 1
    ym_end= 12*end_year + end_month - 1
    for ym in range( ym_start, ym_end ):
        y, m = divmod( ym, 12 )
        yield y, m+1
```

### Border Measure Bundler (Helper Function)
This function receives in rows and bundles entries based on year month per border. Border either can be `US-Canada Border` or `US-Mexico Border` or any other border in your dataset.
```
def border_measure_bundler(entries, year, month, border):
    borders = []
    border_measures = []
    for record in entries:
        date_pattern = re.search(r'([0-9]{1,2})[-/:]([0-9]{1,2})[-/:]([0-9]{4})', record[1])
        standardate  = date_pattern.group(1)+'/'+'01'+'/'+date_pattern.group(3)+' 12:00:00 AM'
        record_date = datetime.strptime(standardate, '%m/%d/%Y %I:%M:%S %p')
        if (year == record_date.year) and (month == record_date.month):
            if record[0] == border:
                borders = [record[0],record[1]]
                border_measures.append(record[2:4])
    if borders:
        return borders
```

### Border Averages Aggregator (Main Function)
Main function uses dictionaries and cumulatively aggregates monthly `Measure` s and `Value` s then devides per their occurence resulting in running averages.
```
def border_averages_aggregator(ascending_data, *borders):
    results = []
    date_format = '%m/%d/%Y %I:%M:%S %p'
    for border in borders:
        accumulator = {}
        start = datetime.strptime(ascending_data[-1][1], date_format)
        end = datetime.strptime(ascending_data[0][1], date_format)
        for date in month_year_iterator( start.month, start.year, end.month + 1, end.year):
            try:
                if date:
                    this_record = border_measure_bundler(ascending_data, date[0], date[1], border, date_format)
                    this_measure = this_record[-1]
                    for key,value in this_measure.items():
                        accumulator.setdefault(key, []).append(value)
                    for k, v in accumulator.items():
                        if k in this_measure.keys():
                            try:
                                results.append([ this_record[0],this_record[1], k, v[-1], int(Decimal( ( sum(v)-v[-1] ) / (len(v)-1) ).to_integral_value(rounding=ROUND_HALF_UP) )  ])
                            except:
                                results.append([ this_record[0],this_record[1], k, v[-1], 0  ])
            except:
                None
    return results
```

## Instructions

### Prerequisites
This program is written in `Python` version `3`. To install latest `Python 3` or for instructions how to install [visit Python's official download page](https://www.python.org/downloads/). This program does not use any `pip` packages and libraries such as `pandas`, `numpy`; except `csv`, `datetime`, `re` and `decimal` (for bankers rounding strategy) which are built in and already available with `Python` installation.

### Preparing the Input Data
Before running the program please make sure your input data has corresponding rows for headers `Border`, `Data`, `Measure` and `Value`. If your input data has different names for columns, you need to chage their names to `Border`, `Data`, `Measure` and `Value`. Otherwise the program will fail, since it does not know where to look for those information.

### Running the Program
Place your input `csv` file into `input` folder in root directory and rename it as `Border_Crossing_Entry_Data.csv`. From terminal while you are in `cd` root, run `./run.sh`. By default input data in the input folder is the whole dataset downloaded from [transportation.gov](https://data.transportation.gov/api/views/keg4-3bc2/rows.csv?accessType=DOWNLOAD) and dates from August 23, 2019. If you want to run the whole dataset no need to change the `csv` file. It will approximately take 30 minutes to run whole dataset of ~350K rows.
> If you encounter permission error running `bash`, allow execution of the program with bash script by `chmod +x run.sh`

### Tests

#### test_1
Default test sample. Small row size. `[PASSED]`

#### test_2
Yearly data from wide gap 2002 - 2017 and records from dates 2002, 2017, 2018, 2019 randomly followed by each other. `[PASSED]`

#### test_3
Unordered columns and duplicated `Date`, columns. Strings in `Measure` have lower case and uppercase typos. Test also have `Others` type of measure. `[PASSED]`

#### test_4
Date field has no AM PM indicator. Month, Day, Year seperator varies. Month has no `0` such as instead of `05` `5`, instead of `09`, `9`. Test also includes with different day of the month such as `9/21/2019`. `[PASSED]`

## Notes
Current program algorithm for processing rows [shows](https://plot.ly/~uxdom/1) `O(nlogn)` type of complexity.

## License
MIT License

Copyright (c) 2019 Ali Celik

Permission is hereby granted, free of charge, to any person obtaining a copyof this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.