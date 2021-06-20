
import geocoder
import pandas as pd
import streamlit as st
import yfinance as yf
from bs4 import BeautifulSoup
import requests


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
            self.ticker_list = self.ticker_list[["Name","Symbol"]]\
                                .replace("Inc. Class A Common Stock","",regex=True)\
                                .replace("Inc. Common Stock","",regex=True).replace("Common Stock","",regex=True)\
                                .replace("Common Stock","",regex=True).replace("Inc Common Stock","",regex=True)\
                                .replace("Inc.","",regex=True)
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
        
        with st.spinner('Now Loading...'):
            for comp, ticker in selected_ticker_comp.items():
                self.stock_info = yf.Ticker(ticker)
                
                self.price_hist = self.stock_info.history(period=f"{days}d")
                self.price_hist = self.price_hist.loc[:,["Close"]]
                self.price_hist = self.price_hist.rename(columns={"Close":comp})
                
                self.all_stockinfo = pd.concat([self.all_stockinfo,self.price_hist],axis=1).sort_index(ascending=False)
            
            if selected_ticker_comp:
                self.all_stockinfo.index = self.all_stockinfo.index.strftime("%Y/%m/%d")
                st.write(f"Stock Price in {days}")
                st.dataframe(self.all_stockinfo)
                st.line_chart(self.all_stockinfo)
                

    def showLocation(self, selected_ticker_comp:dict) ->None:
        with st.spinner('Now Loading...'):
            self.all_location = pd.DataFrame()
            
            for comp, ticker in selected_ticker_comp.items():
                self.stock_info = yf.Ticker(ticker)
                
                self.location = self.stock_info.info["address1"]
                self.ret = geocoder.osm(self.location, timeout=1.0)
                self.location = pd.DataFrame(self.ret.latlng)
                self.location = self.location.T.set_axis(['lat', 'lon'], axis=1)
                self.all_location = pd.concat([self.all_location,self.location])
            
            if not self.all_location.empty:
                st.write("Location Of The Selected Conmanies")
                st.map(self.all_location)
                
                
    def getNews(self, selectedComps:list)->None:
        for comp in selectedComps:
            self.yf_page = f"https://finance.yahoo.co.jp/news/search/?q={comp}&queryType=orQuery&category=bus_all"
            self.res = requests.get(self.yf_page)
            self.soup = BeautifulSoup(self.res.text,"html.parser")
            
            #Newsがあるか判定。NoneであればNewsがある。
            if self.soup.find("p",{"class":"_3dVFfhRc"}) == None:
                self.conts = self.soup.find("ul",{"class":"_2U3CbQRW _3FDiuD5H"})
                self.conts_lists = self.conts.find_all("li")
            
                self.news_df = pd.DataFrame()
                self.news_dict = {}
                for self.conts_list in self.conts_lists:
                    if self.conts_list.find("span",{"class":"_36K6k1hY"}) and self.conts_list.find_all("span",{"class":"_1gx5TnFY"})[-1].text == "Bloomberg":
                        self.news_dict[self.conts_list.find("span",{"class":"_36K6k1hY"}).text] = self.conts_list.find("a")["href"]
        
                st.success(f'Following are "{comp}" News')
                for self.news_title, self.news_url in self.news_dict.items():
                    st.text(self.news_title)
                    st.markdown((self.news_url))
                    
                    
            #newsがない場合
            elif self.soup.find("p",{"class":"_3dVFfhRc"}).text == "該当するニュースが見つかりません。":
                st.warning(f'No news about "{comp}" !!!')
           
                
                



if __name__ == "__main__":
    past = PastSockPrice()


    #全会社のティッカーを取得
    all_ticker_dict = past.createAllTickerDict(past.ticker_files)

    #sidebarの作成
    st.sidebar.markdown('__[Chose a Period]__')
    days = st.sidebar.slider(
        '',0, 100, 7
    )

    st.sidebar.markdown('__[Select Companies]__')
    selectedComps = st.sidebar.multiselect(
        "",sorted(past.showCompName(all_ticker_dict))
    )

    #選択された会社名のティッカーを取得
    selected_ticker_comp_dict = past.createTickerDict(all_ticker_dict,selectedComps)

    #選択されたティッカーの株価情報を表示
    past.showStockPrice(selected_ticker_comp_dict,all_ticker_dict)

    #会社の場所をマップ表示
    location_checkbox = st.sidebar.checkbox("Show Location Of The Companies")
    if location_checkbox:
        past.showLocation(selected_ticker_comp_dict)

    contact = st.sidebar.write(
        '<span style="color:gray;"><small>[Contact]</small></span><br>'
        '<span style="color:gray"><small>jyukiwave@gmail.com</small></span>',
        unsafe_allow_html=True
    )

    #選択された会社のニュース情報をスクレイピング
    past.getNews(selectedComps)
