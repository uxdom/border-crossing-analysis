import csv, re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
# Due to bankers rounding in calculating averages 
# Rounding strategy changed with Decimal

# Csv loader function
# Collects csv data into dictionary and then writes into records
def csv_to_dict_loader(source, columns):
    records = []
    with open(SOURCE_CSV, mode = "r") as file:
        csv_reader = csv.DictReader(file)
        line_count = 0
        for row in csv_reader:
            record = []
            date_pattern = re.search(r'([0-9]{1,2})[-/:]([0-9]{1,2})[-/:]([0-9]{4})', row['Date'])
            # standardize date assigning single day with 
            # (pattern group 1) / 01 / (pattern group 3) 12:00:00 AM
            # Patch month without zeros
            if len(str(date_pattern.group(1))) == 2:
                standardate  = date_pattern.group(1)+'/'+'01'+'/'+date_pattern.group(3)+' 12:00:00 AM'
            else:
                standardate  = '0'+date_pattern.group(1)+'/'+'01'+'/'+date_pattern.group(3)+' 12:00:00 AM'
            row['Date'] = standardate
            for col in columns:
                try:
                    record.append(row[col.title()])
                except KeyError:
                    pass
            records.append(record)
            line_count += 1
        file.close()
    # Returns yearly ascending sort of processed rows
    return sorted(records, key=lambda x: datetime.strptime(x[1], '%m/%d/%Y %I:%M:%S %p' ), reverse=True)

# Unique Counter counts similar measures and creating a set of sums
# A list of mesure, values are collected into dict unique keys
def unique_value_counter(list):
    sums = {}
    for means, val in list:
        means = means.title()
        if means in sums:
            sums[means] += int(val)
        else:
            sums[means] = int(val)
    if sums:
        # Returns dictionary of sums --note-- can be tupled as sorted(sums.items())
        return sums

# Month and year iterator
# Used to iterate over start and end of given date range
def month_year_iterator(start_month, start_year, end_month, end_year):
    ym_start= 12*start_year + start_month - 1
    ym_end= 12*end_year + end_month - 1
    for ym in range( ym_start, ym_end ):
        y, m = divmod( ym, 12 )
        yield y, m+1


# Data aggregator function that takes in list of rows, year and month 
# Aggregates entries per given border in arguments
def border_measure_bundler(entries, year, month, border):
    # Setting list to collect border total for single year and single month 
    borders = []
    # Measure and values from scanned records
    border_measures = []
    # Going through records and meeting conditions set by extractor function
    for record in entries:
        record_date = datetime.strptime(record[1], '%m/%d/%Y %I:%M:%S %p')
        if (year == record_date.year) and (month == record_date.month):
            # Checking for border and appending its measure and values
            if record[0] == border:
                borders = [record[0],record[1]]
                # Append border measures to list from the scanned records that meets the condition
                border_measures.append(record[2:4])
                #print(record)
    # Calling counter snippet to collect unique measure and summed values and adding to borders
    borders.append(unique_value_counter(border_measures))    
    #print(f'Border totals: {border}')
    if borders:
        # Returs the final row with year, month per border
        return borders


# Border data aggregator with totals and averages
# Border or borders are set to capture from ascending data
def border_averages_aggregator(ascending_data, *borders):
    results = []
    date_format = '%m/%d/%Y %I:%M:%S %p'
    for border in borders:
        accumulator = {}
        # Corresponds to the oldest date in ascending rows data
        start = datetime.strptime(ascending_data[-1][1], date_format)
        # Corresponds to the newest date in ascending rows data
        end = datetime.strptime(ascending_data[0][1], date_format)
        # Iterator in that given range
        for date in month_year_iterator( start.month, start.year, end.month + 1, end.year):
            # Date is returned as tuples year and month as such (2019, 10)
            try:
                # Escaping errors for empty dates in a given year month date range
                if date:
                    # Bundles measures and value sums for that month of the year for the record
                    this_record = border_measure_bundler(ascending_data, date[0], date[1], border)
                    # Locates the measures which is a dictionary
                    this_measure = this_record[-1]
                    for key,value in this_measure.items():
                        # For each measure item in the month append values as months go by
                        accumulator.setdefault(key, []).append(value)
                    # Checking for identical keys in measure : [appended values] 
                    for k, v in accumulator.items():
                        # Get this measure and put averages next to them
                        if k in this_measure.keys():
                            # Building new rows in results with value and average 
                            try:
                                results.append([ this_record[0],this_record[1], k, v[-1], int(Decimal( ( sum(v)-v[-1] ) / (len(v)-1) ).to_integral_value(rounding=ROUND_HALF_UP) )  ])                          
                            except:
                                results.append([ this_record[0],this_record[1], k, v[-1], 0  ])
            except:
                None
    return results

if __name__ == '__main__':

    # Settings 
    SOURCE_CSV = './input/Border_Crossing_Entry_Data.csv'
    COLUMNS = ['Border', 'Date', 'Measure', 'Value']    
    LOAD = csv_to_dict_loader ( SOURCE_CSV, COLUMNS )
    RESULT = border_averages_aggregator( LOAD, 'US-Canada Border', 'US-Mexico Border' )
    FINAL = sorted( RESULT, key=lambda x: ( datetime.strptime(x[1], '%m/%d/%Y %I:%M:%S %p'), x[0], x[2] ), reverse=True )
    # Prepare the report
    with open('./output/report.csv', mode='w') as report:
        csv_writer = csv.writer(report, delimiter=',')
        csv_writer.writerow([x.title() for x in COLUMNS] + ['Average'])
        for row in FINAL:
            csv_writer.writerow(row)
        report.close()
    #print('Output report ready!')
