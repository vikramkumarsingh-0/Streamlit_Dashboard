
import streamlit as st
import plotly.express as px
from ydata_profiling import ProfileReport
import pandas as pd
import os
import warnings


warnings.filterwarnings("ignore")


 

def get_dataframe(file_uploader):
     if file_uploader is not None:
         import os

         import tempfile
#        '''mkstemp:
 #                  mk: make
  #                 s: secure
   #                temp: temporary'''
         fd, path = tempfile.mkstemp() #The tempfile.mkstemp() function is a useful way to create temporary files in a secure manner. The function is easy to use and provides a number of options for customizing #the temporary file.
         try:
             with os.fdopen(fd, 'wb') as tmp:  # Open in binary mode
                 tmp.write(file_uploader.read())
            #  df = pd.read_csv(path, encoding='ISO-8859-1')  # Specify encoding
             df = pd.read_excel(path)  # Specify encoding
         finally:
             os.remove(path)
     else:            
            df = pd.DataFrame()
     return df



def main():
     st.set_page_config(page_title="VickyStore",page_icon=":sparkling_heart:",layout="wide")

     st.markdown('<style>div.block-container{padding-top:1rem;} </style>', unsafe_allow_html=True     )

     st.title(":bar_chart: Sample data set for learning")

     file_uploader = st.file_uploader(":file_folder: upload a file", type=(["csv", "txt", "xlsx", "xls"]))
     

     df = get_dataframe(file_uploader)
     
     #Check columns
       
     col = df.columns
     col_df = pd.DataFrame(col).T
     if df.empty:
              st.write('Uploaded Empty Dataset')
     else:
          st.dataframe(col_df)    
     
     
     # with st.expander("View Data header:"):
     #      df = df.reset_index()
     #      styled_df = df.style.background_gradient(cmap='Blues')
     #      st.write(styled_df)
     #      # csv=styled_df.to_csv(index=False).encode('utf-8')
     #      st.download_button('Download Columns', data=csv ,file_name='data_headers.csv', mime='text/csv')
     









     if df is not None:
          if df.empty:
              st.write('')
          else:
            st.dataframe(df.sample(10))
     col1, col2 = st.columns((2))# Date selector to select the data between date 
     
     if "Order Date" in df.columns:
         df["Order Date"] = pd.to_datetime(df["Order Date"])
         startdate = pd.to_datetime(df["Order Date"]).min()
         enddate = pd.to_datetime(df["Order Date"]).max()
         with col1:
          date1 = pd.to_datetime(st.date_input('Start Date', startdate))
         with col2:
          date2 = pd.to_datetime(st.date_input('End Date', enddate))
         df = df[(df["Order Date"]>=date1)   & (df["Order Date"]<=date2)].copy()
        #  side filter panel to filter data base on reagion, state and city              
     st.sidebar.header("Chose your filter")  
     
     
         
          # Create for region
          
          #this unique for filter should known in advance after uploading i.e I don't known which column could be use for filter.may be for AI.....i.e from dataset my ai detect the buzz words like region,state,city,area,pincode,country,date and time etc  
     region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
     if not region:
          df2 = df.copy()
     else:
          df2 = df[df['Region'].isin(region)]
          
          
               
          # create for state
          
     state = st.sidebar.multiselect("Pick your State", df2["State"].unique())
     if not state:
        df3 = df2.copy()
     else:
          df3 = df2[df2['State'].isin(state)]
          
          
          
     # Create for city
     city = st.sidebar.multiselect("Pick your City", df3["City"].unique())
          # if not city:
          #      df4 = df3.copy()
          # else:
          #      df4= df3[df3['City'].isin(city)]
               
               
          # Filter the data based on Region, State and City
          
     if not region and not state and not city:
          filtered_df = df #if nothing is selected from sidebar
     elif not state and not city:
          filtered_df = df[df['Region'].isin(region)]
     elif not region and not city:
          filtered_df = df[df["State"].isin(state)]
     elif state and city:
          filtered_df = df3[df['State'].isin(state) & df3['City'].isin(city)]
     elif region and city:
          filtered_df = df3[df['Region'].isin(region) & df3['City'].isin(city)]
     elif region and state:
          filtered_df = df3[df['Region'].isin(region) & df3['State'].isin(state)]
     elif city:
          filtered_df = df3[df3['City'].isin(city)]
     else:
          filtered_df = df3[df3['Region'].isin(region) & df3['State'].isin(state)  & df3['City'].isin(city) ]
          
     category_df = filtered_df.groupby(by=['Category'], as_index=False)['Sales'].sum()
          
     with col1:
          st.subheader("Category wise Sales")
          fig = px.bar(category_df, x = 'Category', y='Sales', text = ['Rs {:,.2f}'.format(x) for x in category_df["Sales"]], template = 'seaborn')
          st.plotly_chart(fig, use_container_width=True, height=200)
               
               
     with col2:
          st.subheader("Reagion wise Sales")
          fig=px.pie(filtered_df, values = 'Sales', names = 'Region', hole =0.5)
          fig.update_traces(text = filtered_df['Region'], textposition='outside')
          st.plotly_chart(fig, use_container_width=True)
          
     cl1,cl2 = st.columns((2))
     with cl1:
          with st.expander("Category_ViewData"):
               st.write(category_df.style.background_gradient(cmap="Blues"))
               csv = category_df.to_csv(index=False).encode('utf-8')
               st.download_button("Download Data", data=csv, file_name="Category.csv", mime = "text/csv", help="Click here to download the data as a CSV file")
               
               
     with cl2:
          with st.expander("Region_ViewData"):
               region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
               st.write(region.style.background_gradient(cmap="Oranges"))
               csv = region.to_csv(index=False).encode('utf-8')
               st.download_button("Download Data", data=csv, file_name="Region.csv", mime = "text/csv", help="Click here to download the data as a CSV file")
     
     
     
     filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
     st.subheader('Time Series Analysis')
     
     
     linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
     fig2 = px.line(linechart, x = "month_year", y = "Sales", labels = {"Sales":"Amount"},height=500, width=1000,template="gridon")
     
     # Convert the Plotly Express figure to a Plotly graph_objs.Figure object
     # fig2 = go.Figure(fig2)
     # print(type(fig2))
     # # Connect gaps in the data
     # fig2.update_traces(connectgaps=True)
     
     st.plotly_chart(fig2,use_container_width=True)
     
     with st.expander("View Date of TimeSeries:"):
          st.write(linechart.T.style.background_gradient(cmap="Blues"))
          csv=linechart.to_csv(index=False).encode('utf-8')
          st.download_button('Download Date', data=csv ,file_name='TimeSeries.csv', mime='text/csv')
          
     # Create a trees based on Region, Category, sub-Category    
     st.subheader("Hierarchical view of Sales using TreeMap")
     fig3 = px.treemap(filtered_df, path = ['Region','Category', 'Sub-Category'], values = 'Sales', hover_data = ['Sales'],color = 'Sub-Category' )
     fig3.update_layout(width = 800,height = 650)
     st.plotly_chart(fig3,use_container_width=True)
     
     
          
     chart1,chart2 = st.columns((2))
     with chart1:
          st.subheader("Segment wise Sales")
          fig = px.pie(filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
          fig.update_traces(text = filtered_df['Segment'], textposition ='inside')
          st.plotly_chart(fig,use_container_width=True)
     
     with chart2:
          st.subheader("Category wise Sales")
          fig = px.pie(filtered_df, values = "Sales", names = "Category", template = "plotly_dark")
          fig.update_traces(text = filtered_df['Category'], textposition ='inside')
          st.plotly_chart(fig,use_container_width=True)
     
     
     import plotly.figure_factory as ff
     st.subheader(':point_right: Month wise Sub-Category Sales Summary')
     
     with st.expander("Summary_Table"):
          df_sample = df[0:5][['Region', 'State','City','Category','Sales','Profit','Quantity']]
          fig = ff.create_table (df_sample, colorscale = 'Cividis')
          st.plotly_chart(fig, use_container_width=True)
          
          st.markdown("Month wise sub-Category Table")
          filtered_df['month']=filtered_df['Order Date'].dt.month_name()
          sub_category_Year = pd.pivot_table(data=filtered_df, values = 'Sales', index = ['Sub-Category'], columns = 'month')
          st.write(sub_category_Year.style.background_gradient(cmap="Blues"))
          
     # Create a scatter plot
     
     data1 = px.scatter(filtered_df, x="Sales", y="Profit", size = "Quantity")
     data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.", titlefont = dict(size=20), xaxis = dict(title="Sales", titlefont=dict(size=19)),yaxis=dict(title='Profit', titlefont = dict(size=19)))
     st.plotly_chart(data1,use_container_width=True)
     
     with st.expander("View Data"):
          st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))  
          
          
     #Download original Dataset
     
     csv = df.to_csv(index=False).encode('utf-8')
     st.download_button('Download Data', data = csv, file_name = 'Original_Data.csv', mime='text/csv')
      
     
     
     
     with st.expander("View YData_Profiling"):
          
          dfresult = filtered_df.dropna()
          ydata=ProfileReport(filtered_df, title="Report")
          ydata.to_widgets()
          st.write(ydata)
          
     
     
     
     
     
     



if __name__ == "__main__":
     main()

     
     # Create for zip code
     # zipcode = st.sidebar.multiselect("Pick your Zip Code", df4["ZipCode"].unique())
     # if not zipcode:
     #      df5 = df4.copy()
     # else:
     #      df5= df3[df3['City'].isin(zipcode)]
        
        
#         import plotly.graph_objects as go

# # Your existing code...
# linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
# fig2 = px.line(linechart, x = "month_year", y = "Sales", labels = {"Sales":"Amount"},height=500, width=1000,template="gridon")

#  Convert the Plotly Express figure to a Plotly graph_objs.Figure object
#  fig2 = go.Figure(fig2)

# st.plotly_chart(fig2,use_container_width=True)

        
        
        
        
        
        
        
        
        
        
        
   