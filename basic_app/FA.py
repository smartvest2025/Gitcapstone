import pandas as pd
import datetime
import yfinance as yf

def piotroski(ticker):
    ticker = yf.Ticker(ticker)
    bs = ticker.balance_sheet
    inc = ticker.financials
    cf = ticker.cashflow

    # Debug: Print financial statements
    print("Balance Sheet:\n", bs)
    print("Income Statement:\n", inc)
    print("Cash Flow:\n", cf)

    # Extract metrics
    longTermDebt = bs.loc['Long Term Debt'].iloc[0] if 'Long Term Debt' in bs.index else 0
    longTermDebtPre = bs.loc['Long Term Debt'].iloc[1] if 'Long Term Debt' in bs.index else 0

    totalAssets = bs.loc['Total Assets'].iloc[0] if 'Total Assets' in bs.index else 0
    totalAssetsPre = bs.loc['Total Assets'].iloc[1] if 'Total Assets' in bs.index else 0
    totalAssetsPre2 = bs.loc['Total Assets'].iloc[2] if 'Total Assets' in bs.index and len(bs) > 2 else 0

    currentAssets = bs.loc['Total Current Assets'].iloc[0] if 'Total Current Assets' in bs.index else 0
    currentAssetsPre = bs.loc['Total Current Assets'].iloc[1] if 'Total Current Assets' in bs.index else 0

    currentLiabilities = bs.loc['Total Current Liabilities'].iloc[0] if 'Total Current Liabilities' in bs.index else 0
    currentLiabilitiesPre = bs.loc['Total Current Liabilities'].iloc[1] if 'Total Current Liabilities' in bs.index else 0

    revenue = inc.loc['Total Revenue'].iloc[0] if 'Total Revenue' in inc.index else 0
    revenuePre = inc.loc['Total Revenue'].iloc[1] if 'Total Revenue' in inc.index else 0

    grossProfit = inc.loc['Gross Profit'].iloc[0] if 'Gross Profit' in inc.index else 0
    grossProfitPre = inc.loc['Gross Profit'].iloc[1] if 'Gross Profit' in inc.index else 0

    netIncome = inc.loc['Net Income'].iloc[0] if 'Net Income' in inc.index else 0
    netIncomePre = inc.loc['Net Income'].iloc[1] if 'Net Income' in inc.index else 0

    operatingCashFlow = cf.loc['Total Cash From Operating Activities'].iloc[0] if 'Total Cash From Operating Activities' in cf.index else 0
    operatingCashFlowPre = cf.loc['Total Cash From Operating Activities'].iloc[1] if 'Total Cash From Operating Activities' in cf.index else 0

    commonStock = bs.loc['Common Stock'].iloc[0] if 'Common Stock' in bs.index else 0
    commonStockPre = bs.loc['Common Stock'].iloc[1] if 'Common Stock' in bs.index else 0

    # Calculate criteria
    denominator = (totalAssets + totalAssetsPre) / 2
    ROAFS = int(netIncome / denominator > 0) if denominator != 0 else 0

    CFOFS = int(operatingCashFlow > 0)
    ROADFS = int(netIncome / ((totalAssets + totalAssetsPre) / 2)) > (netIncomePre / ((totalAssetsPre + totalAssetsPre2) / 2)) if totalAssetsPre2 != 0 else 0
    CFOROAFS = int((operatingCashFlow / totalAssets) > (netIncome / denominator)) if totalAssets != 0 and denominator != 0 else 0

    LTDFS = int(longTermDebt <= longTermDebtPre)
    CRFS = int((currentAssets / currentLiabilities) > (currentAssetsPre / currentLiabilitiesPre)) if currentLiabilities != 0 and currentLiabilitiesPre != 0 else 0
    NSFS = int(commonStock <= commonStockPre)
    GMFS = int((grossProfit / revenue) > (grossProfitPre / revenuePre)) if revenue != 0 and revenuePre != 0 else 0
    ATOFS = int((revenue / ((totalAssets + totalAssetsPre) / 2)) > (revenuePre / ((totalAssetsPre + totalAssetsPre2) / 2))) if totalAssetsPre2 != 0 else 0

   

    return ROAFS + CFOFS + ROADFS + CFOROAFS + LTDFS + CRFS + NSFS + GMFS + ATOFS

# Test the function
#print("Piotroski F-Score:", piotroski('MSFT'))