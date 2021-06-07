import geocoder
import pandas as pd
import streamlit as st
import yfinance as yf


from typing import List


class PastSockPrice(object):
    
    def __init__ (self) ->None:
        self.ticker_files = ["nasdaq","myse","amex"]
    
    
    @st.cache
    def createAllTickerDict(self, ticker_files:List) ->dict:
        self.ticker_list = pd.DataFrame()
        for ticker_file in ticker_files:
            tickers = pd.read_csv(f"./tickers/{ticker_file}.csv")
            
            self.ticker_list = pd.concat([self.ticker_list,tickers])
            self.ticker_list = self.ticker_list[["Name","Symbol"]]
            self.all_ticker_dict = dict(self.ticker_list[["Name","Symbol"]].values)
        
        return self.all_ticker_dict


    @st.cache
    def showCompName(self, ticker_dict:dict) ->list:
        self.compName_list = []
        for compName in ticker_dict.keys():
            self.compName_list.append(compName)

        return self.compName_list


    def createTickerDict(self, all_ticker_dict:dict, selectedComps:list) ->dict:
        self.selected_ticker_comp_dict = {}
        for comp in selectedComps:
            self.ticker = all_ticker_dict.get(comp)
            self.selected_ticker_comp_dict[comp] = self.ticker
        return self.selected_ticker_comp_dict
        
    
    def showStockPrice(self, selected_ticker_comp:dict,ticker_dict:dict) ->None:
        self.all_stockinfo = pd.DataFrame()
        
        with st.spinner('Loading!!!'):
            for comp, ticker in selected_ticker_comp.items():
                self.stock_info = yf.Ticker(ticker)
                
                self.price_hist = self.stock_info.history(period=f"{days}d")
                self.price_hist = self.price_hist.loc[:,["Close"]]
                
                self.price_hist = self.price_hist.rename(columns={"Close":comp})
                self.all_stockinfo = pd.concat([self.all_stockinfo,self.price_hist],axis=1)
            
            if selected_ticker_comp:
                self.all_stockinfo.index = self.all_stockinfo.index.strftime("%Y/%m/%d")
                st.dataframe(self.all_stockinfo)
                st.line_chart(self.all_stockinfo)
                

    def showLocation(self, selected_ticker_comp:dict) ->None:
        with st.spinner('Loading!!!'):
            self.all_location = pd.DataFrame()
            
            for comp, ticker in selected_ticker_comp.items():
                self.stock_info = yf.Ticker(ticker)
                
                self.location = self.stock_info.info["address1"]
                self.ret = geocoder.osm(self.location, timeout=1.0)
                self.location = pd.DataFrame(self.ret.latlng)
                self.location = self.location.T.set_axis(['lat', 'lon'], axis=1)
                self.all_location = pd.concat([self.all_location,self.location])
            
            if not self.all_location.empty:
                st.map(self.all_location)


past = PastSockPrice()

#全会社のティッカーを取得
all_ticker_dict = past.createAllTickerDict(past.ticker_files)



#sidebarの作成
days = st.sidebar.slider(
    '■ 表示日数', 0, 100, 7
)

selectedComps = st.sidebar.multiselect(
    "■ 会社を選んでください。",sorted(past.showCompName(all_ticker_dict))
)



#選択された会社名のティッカーを取得
selected_ticker_comp_dict = past.createTickerDict(all_ticker_dict,selectedComps)


#選択されたティッカーの株価情報を表示
past.showStockPrice(selected_ticker_comp_dict,all_ticker_dict)

#会社の場所をマップ表示
location_checkbox = st.sidebar.checkbox("Show location")
if location_checkbox:
    past.showLocation(selected_ticker_comp_dict)

contact = st.sidebar.write(
    '<span style="color:gray;">■ Contact</span><br>'
    '<span style="color:gray">jyukiwave@gmail.com</span>',
    unsafe_allow_html=True
)
