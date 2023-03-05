import xml.etree.ElementTree as ET # https://docs.python.org/3/library/xml.etree.elementtree.html
import csv

broker_dealer = ""
year = 0
qtr = 0

cumulative_market_order_PFOF = 0
cumulative_marketable_limit_order_PFOF = 0
cumulative_nonmarketable_limit_order_PFOF = 0
cumulative_other_order_PFOF = 0

cumulative_sp500_PFOF = 0
cumulative_non_sp500_PFOF = 0
cumulative_options_PFOF = 0

cumulative_venue_PFOF = {}
all_rows = []


class VenueData:
    def __init__(self, year, month, venue_name, security_type, written_disclosure, 
            non_directed_order_pct, market_order_pct, marketable_limit_order_pct, nonmarketable_limit_order_pct, other_order_pct,
            market_order_PFOF, marketable_limit_order_PFOF, nonmarketable_limit_order_PFOF, other_order_PFOF,
            market_order_PFOF_cph, marketable_limit_order_PFOF_cph, nonmarketable_limit_order_PFOF_cph, other_order_PFOF_cph):
        self.year = year
        self.month = month
        self.venue_name = venue_name
        self.security_type = security_type
        self.written_disclosure = written_disclosure
        self.non_directed_order_pct = non_directed_order_pct
        self.market_order_pct = market_order_pct
        self.marketable_limit_order_pct = marketable_limit_order_pct
        self.nonmarketable_limit_order_pct = nonmarketable_limit_order_pct
        self.other_order_pct = other_order_pct
        self.market_order_PFOF = market_order_PFOF
        self.marketable_limit_order_PFOF = marketable_limit_order_PFOF
        self.nonmarketable_limit_order_PFOF = nonmarketable_limit_order_PFOF
        self.other_order_PFOF = other_order_PFOF
        self.market_order_PFOF_cph = market_order_PFOF_cph
        self.marketable_limit_order_PFOF_cph = marketable_limit_order_PFOF_cph
        self.nonmarketable_limit_order_PFOF_cph = nonmarketable_limit_order_PFOF_cph
        self.other_order_PFOF_cph = other_order_PFOF_cph
        
        
def format_number(num):
    return f"{round(num):,}"


def parse(path):
    tree = ET.parse(path)
    root = tree.getroot()

    for metadata in root:
        if metadata.tag == "bd":
            global broker_dealer
            broker_dealer = metadata.text
        if metadata.tag == "year":
            global year
            year = metadata.text
        if metadata.tag == "qtr":
            global qtr
            qtr = metadata.text
        # if metadata.tag != "rMonthly":
        #     print(metadata.tag + ": " + metadata.text)
        else:
            parse_months(metadata) #should be called 3 times (each month in the quarter)


def parse_months(months):
    year = 0
    month = 0
    for month_data in months:
        # print(month_data.tag + ": " + month_data.text) # either "year" or "mon[th]" tag
        if month_data.tag == "year":
            year = month_data.text
        elif month_data.tag == "mon":
            month = month_data.text
        elif month_data.tag in ["rSP500", "rOtherStocks", "rOptions"]:
            # print(month_data.tag) # "rSP500", "rOtherStocks", "rOptions"
            venues = month_data.find("rVenues") #contains list of all venues

            parse_venues(venues, month_data.tag, year, month)
                                    # ^ is security_type


def parse_venues(venues, security_type, year, month):
    for venue in venues:

        venue_name = "" #name of the wholesale market maker
        written_disclosure = "" #a couple of sentences that disclosures the nature of the relationship

        # under the "venue" section of a Form 606 report, there are 3 categories of data:
        # 1. what % of these orders were filled by this venue?
        # 2. how much did a broker receive in PFOF from this venue?
        # 3. how much PFOF was received per 100 shares (for stocks) or 1 option contract (for options)?
        
        # 1
        non_directed_order_pct = 0 
        market_order_pct = 0
        marketable_limit_order_pct = 0
        nonmarketable_limit_order_pct = 0
        other_order_pct = 0

        # 2 & 3
        market_order_PFOF = 0
        market_order_PFOF_cph = 0 # cph = PFOF received for 100 shares or 1 options contract
        
        marketable_limit_order_PFOF = 0
        marketable_limit_order_PFOF_cph = 0
        
        nonmarketable_limit_order_PFOF = 0
        nonmarketable_limit_order_PFOF_cph = 0
        
        other_order_PFOF = 0
        other_order_PFOF_cph = 0

        for venue_data in venue:
            if venue_data.tag == "name":
                venue_name = venue_data.text
            elif venue_data.tag == "materialAspects":
                written_disclosure = venue_data.text

            # all other tags will be #s; let's see if it can be caste to float
            data = 0.0
            try:
                data = float(venue_data.text)
            except:
                continue

            if venue_data.tag == "orderPct":
                non_directed_order_pct = data
            elif venue_data.tag == "marketPct":
                market_order_pct = data
            elif venue_data.tag == "marketableLimitPct":
                marketable_limit_order_pct = data
            elif venue_data.tag == "nonMarketableLimitPct":
                nonmarketable_limit_order_pct = data
            elif venue_data.tag == "otherPct":
                other_order_pct = data

            elif venue_data.tag == "netPmtPaidRecvMarketOrdersUsd":
                market_order_PFOF = data
            elif venue_data.tag == "netPmtPaidRecvMarketOrdersCph":
                market_order_PFOF_cph = data

            elif venue_data.tag == "netPmtPaidRecvMarketableLimitOrdersUsd":
                marketable_limit_order_PFOF = data
            elif venue_data.tag == "netPmtPaidRecvMarketableLimitOrdersCph":
                marketable_limit_order_PFOF_cph = data
                
            elif venue_data.tag == "netPmtPaidRecvNonMarketableLimitOrdersUsd":
                nonmarketable_limit_order_PFOF = data
            elif venue_data.tag == "netPmtPaidRecvNonMarketableLimitOrdersCph":
                nonmarketable_limit_order_PFOF_cph = data

            elif venue_data.tag == "netPmtPaidRecvOtherOrdersUsd":
                other_order_PFOF = data
            elif venue_data.tag == "netPmtPaidRecvOtherOrdersCph":
                other_order_PFOF_cph = data

        # finished parsing data for this specific venue; log the data
        data_from_venue = VenueData(
            year, month, venue_name, security_type, written_disclosure, 
            non_directed_order_pct, market_order_pct, marketable_limit_order_pct, nonmarketable_limit_order_pct, other_order_pct,
            market_order_PFOF, marketable_limit_order_PFOF, nonmarketable_limit_order_PFOF, other_order_PFOF,
            market_order_PFOF_cph, marketable_limit_order_PFOF_cph, nonmarketable_limit_order_PFOF_cph, other_order_PFOF_cph)
        
        bookkeep(data_from_venue)
        



def bookkeep(venue_data):
    """
    Record data found in one rVenue entry, which contains the following data:
        [key]: [possible values]
        venue:  CITADEL SECURITIES LLC    Virtu Americas, LLC    G1X Execution Services, LLC     Two Sigma Securities, LLC   The Nasdaq Stock Market     Jane Street Capital
        order_type: market order, marketable limit order, non-marketable limit order and other orders
        security_type: S&P 500, non-S&P 500, or Options
        PFOF_amount: Int
        PFOF_per_100: PFOF received per 100 shares, or 1 options contract
    """

    # keep a running sum of PFOF categories
    global cumulative_market_order_PFOF
    global cumulative_marketable_limit_order_PFOF
    global cumulative_nonmarketable_limit_order_PFOF
    global cumulative_other_order_PFOF

    global cumulative_sp500_PFOF
    global cumulative_non_sp500_PFOF
    global cumulative_options_PFOF

    global cumulative_venue_PFOF

    # categorize by order_type
    cumulative_market_order_PFOF += venue_data.market_order_PFOF
    cumulative_marketable_limit_order_PFOF += venue_data.marketable_limit_order_PFOF
    cumulative_nonmarketable_limit_order_PFOF += venue_data.nonmarketable_limit_order_PFOF
    cumulative_other_order_PFOF += venue_data.other_order_PFOF

    # categorize by security_type
    PFOF_for_venue_for_security_type_for_period = venue_data.market_order_PFOF + venue_data.marketable_limit_order_PFOF + venue_data.nonmarketable_limit_order_PFOF + venue_data.other_order_PFOF
    if venue_data.security_type == "rSP500":
        cumulative_sp500_PFOF += PFOF_for_venue_for_security_type_for_period
    elif venue_data.security_type == "rOtherStocks":
        cumulative_non_sp500_PFOF += PFOF_for_venue_for_security_type_for_period
    elif venue_data.security_type == "rOptions": 
        cumulative_options_PFOF += PFOF_for_venue_for_security_type_for_period
    else:
        Exception(f"{venue_data.security_type} is not a security type that I understand.")
    
    # categorize by venue type
    if PFOF_for_venue_for_security_type_for_period:
        cumulative_venue_PFOF[venue_data.venue_name] = cumulative_venue_PFOF.get(venue_data.venue_name, 0) + PFOF_for_venue_for_security_type_for_period
    
    # store all entries
    if PFOF_for_venue_for_security_type_for_period != 0.0:
        all_rows.append(venue_data)
    


def print_results_and_write_to_csv(path):
    print("parsed file: {}".format(path))
    print("{} -- Q{} {}".format(broker_dealer, qtr, year))

    print("")
    total_PFOF = cumulative_market_order_PFOF + cumulative_marketable_limit_order_PFOF + cumulative_nonmarketable_limit_order_PFOF + cumulative_other_order_PFOF
    print('Total PFOF: {}'.format(f"{round(total_PFOF):,}"))

    print("")
    print("PFOF by order type:")
    print("cumulative_market_order_PFOF: {}".format(format_number(cumulative_market_order_PFOF)))
    print("cumulative_marketable_limit_order_PFOF: {}".format(format_number(cumulative_marketable_limit_order_PFOF)))
    print("cumulative_nonmarketable_limit_order_PFOF: {}".format(format_number(cumulative_nonmarketable_limit_order_PFOF)))
    print("cumulative_other_order_PFOF: {}".format(format_number(cumulative_other_order_PFOF)))
    total_PFOF_by_order_type = cumulative_market_order_PFOF + cumulative_marketable_limit_order_PFOF + cumulative_nonmarketable_limit_order_PFOF + cumulative_other_order_PFOF
    if round(total_PFOF_by_order_type) != round(total_PFOF):
        print(f"total_PFOF_by_order_type != total_PFOF; {round(total_PFOF_by_order_type)} != {round(total_PFOF)}")

    print("")
    print("PFOF by security type:")
    print("cumulative_sp500_PFOF: {}".format(format_number(cumulative_sp500_PFOF)))
    print("cumulative_non_sp500_PFOF: {}".format(format_number(cumulative_non_sp500_PFOF)))
    print("cumulative_options_PFOF: {}".format(format_number(cumulative_options_PFOF)))
    total_PFOF_by_security_type = cumulative_sp500_PFOF + cumulative_non_sp500_PFOF + cumulative_options_PFOF
    if round(total_PFOF_by_security_type) != round(total_PFOF):
        print(f"total_PFOF_by_security_type != total_PFOF; {round(total_PFOF_by_security_type)} != {round(total_PFOF)}")

    print("")
    print("PFOF by execution venue:")
    total_PFOF_by_execution_venue = 0
    for venue, PFOF_amount in sorted(cumulative_venue_PFOF.items()):
        total_PFOF_by_execution_venue += PFOF_amount
        print("{}: {}".format(venue, format_number(PFOF_amount)))

    if round(total_PFOF_by_execution_venue) != round(total_PFOF):
        print(f"total_PFOF_by_execution_venue != total_PFOF; {round(total_PFOF_by_execution_venue)} != {round(total_PFOF)}")


    write_csv_row([year, qtr, f"{round(total_PFOF):,}", format_number(cumulative_market_order_PFOF), 
            format_number(cumulative_marketable_limit_order_PFOF),
            format_number(cumulative_nonmarketable_limit_order_PFOF),
            format_number(cumulative_other_order_PFOF),
            "",
            format_number(cumulative_sp500_PFOF),
            format_number(cumulative_non_sp500_PFOF),
            format_number(cumulative_options_PFOF)])
    print("--------------------------------------------------")


def write_csv_row(row):
    with open('quarterly_data.csv', 'a') as csv_writer:
        writer = csv.writer(csv_writer)
        writer.writerow(row)


def main(year, write_only_PFOF):
    # clear the csv file is no longer necessary?
    FORM_606_FOLDER = "Form_606s"
    files_parsed = []
    
    for quarter in range(1, 5):
        # make sure to cd into the project's directory before running `python3 parse-form-606.py`
        
        # TDA = "../../Desktop/PFOF/TDA-606/tdainc-TDA2055-q{}-2021.xml".format(i) 
        # vanguard_q4_2021 = "../../Desktop/PFOF/Disclosure_Report_Vanguard Brokerage Services_2021Q4.xml" # 0
        HOOD = f"{FORM_606_FOLDER}/HOOD-{year}/606-HOOD-2022Q{quarter}.xml" #robinhood
        APEX = f"{FORM_606_FOLDER}/APEX-{year}/606-APEX-2022Q{quarter}.xml"
        IBKR = f"{FORM_606_FOLDER}/IBKR-{year}/IBKR_606a_2022_Q{quarter}.xml" 
        # GSCO = f"{FORM_606_FOLDER}/GSCO-{year}-GSCO_606_{quarter}_{year}_{.....}.xml" #goldman sachs
        SCHW = f"{FORM_606_FOLDER}/SCHW/606-CHAS-{year}Q{quarter}.xml"
        
        # path = APEX
        # path = IBKR
        path = HOOD
        # path = SCHW
        output_file_name = "robinhood"
        
        print(f"Now parsing path {path}")
        parse(path)
        print_results_and_write_to_csv(path)
        files_parsed.append(path)
    
    # write output csv
    if write_only_PFOF:
        csv_output_name = f'form_606_{output_file_name}_PFOF_only.csv'
    else:
        csv_output_name = f'form_606_{output_file_name}_all_data.csv'

    with open(csv_output_name, 'w') as csv_writer:
        HEADER_ONLY_PFOF_DATA = [
            "year", "month", "venue_name", "security_type", "",
            "market_order_PFOF", "marketable_limit_order_PFOF", "nonmarketable_limit_order_PFOF", "other_order_PFOF"]

        HEADER_ALL_DATA = [
            "year", "month", "venue_name", "security_type", "",
            "non_directed_order_pct", "market_order_pct", "marketable_limit_order_pct", "nonmarketable_limit_order_pct", "other_order_pct", "",
            "market_order_PFOF", "marketable_limit_order_PFOF", "nonmarketable_limit_order_PFOF", "other_order_PFOF", "",
            "market_order_PFOF_cph", "marketable_limit_order_PFOF_cph", "nonmarketable_limit_order_PFOF_cph", "other_order_PFOF_cph", "",
            "written_disclosure"]
        
        writer = csv.writer(csv_writer)
        if write_only_PFOF:
            writer.writerow(HEADER_ONLY_PFOF_DATA)
        else:
            writer.writerow(HEADER_ALL_DATA)

        for venue_data in all_rows:
            #translate security_type
            security_type = ""
            if venue_data.security_type == "rSP500":
                security_type = "S&P 500 stocks"
            elif venue_data.security_type == "rOtherStocks":
                security_type = "non-S&P 500 stocks"
            elif venue_data.security_type == "rOptions":
                security_type = "options"
            else:
                Exception("unknown security_type")
        
            payload = ""
            if write_only_PFOF:
                payload = [
                    venue_data.year, venue_data.month, venue_data.venue_name, security_type, "",
                    venue_data.market_order_PFOF, venue_data.marketable_limit_order_PFOF, venue_data.nonmarketable_limit_order_PFOF, venue_data.other_order_PFOF]
            else:
                payload = [    
                    venue_data.year, venue_data.month, venue_data.venue_name, security_type, "",    
                    venue_data.non_directed_order_pct, venue_data.market_order_pct, venue_data.marketable_limit_order_pct, venue_data.nonmarketable_limit_order_pct, venue_data.other_order_pct, "",
                    venue_data.market_order_PFOF, venue_data.marketable_limit_order_PFOF, venue_data.nonmarketable_limit_order_PFOF, venue_data.other_order_PFOF, "",    
                    venue_data.market_order_PFOF_cph, venue_data.marketable_limit_order_PFOF_cph, venue_data.nonmarketable_limit_order_PFOF_cph, venue_data.other_order_PFOF_cph, "",   
                    venue_data.written_disclosure]

            writer.writerow(payload)

    print("")
    print(f'Wrote {csv_output_name} after having parsed through the following files')
    for i, file in enumerate(files_parsed):
        print(f' #{i+1}: {file}')


# under the "venue" section of a Form 606 report, there are 3 categories of data:
    # 1. what % of these orders were filled by this venue?
    # 2. how much did a broker receive in PFOF from this venue?
    # 3. how much PFOF was received per 100 shares (for stocks) or 1 option contract (for options)?
        
# write_only_PFOF=True writes only category #2
# write_only_PFOF=False writes all 3 categories

main(year=2022, write_only_PFOF=False)