import streamlit as st
# st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
# from plotly import graph_objs as go


import functions as f



## run this for a new game
# df = pd.DataFrame(columns=['nb Fields', 'Crop 1', 'Crop 2', 'Crop 3', 'Crop 4', 'Cover', 'Structure', 'N need'])
# df.to_csv('app.csv')


fname1 = 'CY.csv'
fname2 = 'NY.csv'
fname3 = 'RNI.csv'
fname4 = 'UL.csv'
fname5 = 'crop_char_sep.csv'
fname6 = 'crop_char.csv'
fname7 = 'sequences.csv'


CY,NY,RNI,UL,crop_char_sep,crop_char,df_CS = f.load_data(fname1,fname2,fname3,fname4,fname5,fname6,fname7)
Crops_list = list(pd.read_csv('list_of_crops.csv').values[:,1])
Nutrients_list = list(pd.read_csv('list_of_Nutrients.csv').values[:,0])
df = pd.read_csv('app_opt.csv',index_col=0)




maxFields = 1500
names = ['Cereal & Grains','Green vegetables','Pulses & Vegetables','Oils & Fats']
names_char  = ['Cover', 'Structure', 'N need']
opt_value = 40
min_cover = -1.83
min_struc = -.167
max_N     = 1.75

########################################################################################################
# APP
# section[data-testid="stSidebar"].css-ng1t4o{{width: 14rem;}}
st.set_page_config( page_title="Game Thesis Mark", 
                    layout="wide"
                )

st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 500px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 500px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


page = st.sidebar.selectbox('Select page', ['Guideline', 'Game', 'Data'])
form = st.sidebar.form(key="annotation")

with form:

    cols = st.columns(1)
    nbfields = cols[0].slider("Number of Fields:", 1, int(maxFields-sum(df['nb Fields'].values)), 1)
    cols = st.columns(2)
    crop1 = cols[0].selectbox("Crop 1", Crops_list)
    crop2 = cols[1].selectbox("Crop 2", Crops_list)
    cols = st.columns(2)
    crop3 = cols[0].selectbox("Crop 3", Crops_list)
    crop4 = cols[1].selectbox("Crop 4", Crops_list)
    
    submitted = st.form_submit_button(label="Submit")
    st.write("")
    num = st.number_input("Pick a row number that has to be deleted",min_value=0,max_value=len(df))
    deleted = st.form_submit_button(label="Delete")
    st.write("")
    st.write("Click the reset button to start with a clean sheet")
    resetted = st.form_submit_button(label="Reset")

if deleted:
    df = df.drop(num,axis=0)
    df = df.reset_index(drop=True)
    # df = df.drop(['index'], axis=1)
    df.to_csv('app.csv')

if resetted:
    df = pd.DataFrame(columns=['nb Fields', 'Crop 1', 'Crop 2', 'Crop 3', 'Crop 4', 'Cover', 'Structure', 'N need'])
    df.to_csv('app.csv')

if submitted:

    df_added_crops = pd.DataFrame(columns=['Crop 1','Crop 2','Crop 3','Crop 4'])
    df_added_crops = df_added_crops.append({'Crop 1' : crop1, 'Crop 2' : crop2, 'Crop 3' : crop3, 'Crop 4' : crop4},ignore_index=True)

    seq_nr = f.DefineSequenceNumber(df_added_crops, df_CS)[0]
    if seq_nr == -1:
        st.error('The crop sequence contains two or more crops of the same family')
    else:

        row = {'nb Fields' : nbfields,
                'Crop 1' : crop1, 'Crop 2' : crop2, 'Crop 3' : crop3, 'Crop 4' : crop4,
                    'Cover' : crop_char[seq_nr,0],
                    'Structure' : crop_char[seq_nr,1], 
                    'N need' : crop_char[seq_nr,2]
                }

        df = df.append(row, ignore_index=True)

        seqs = f.DefineSequenceNumber(df, df_CS)
        fields = df['nb Fields'].values

        NY_total, CY_total = f.getYield(seqs, fields, NY, CY)

        percentages_NY, theta = f.getPercentages(NY_total, RNI)

        # check for different groups
        check = f.check_max(seqs,fields,NY,CY)

        # # check for crop characteristics
        # check_char = f.check_char(seq_nr,crop_char,[min_cover,min_struc,max_N])

        # # check for upper limit
        # check_UL = f.check_UL(percentages_NY, UL)

        if (sum(check) == 0): # & (sum(check_char) == 0):

            df.to_csv('app.csv')

            st.success("Thanks! Your crop sequence was added.")


        # if statements for number of groups
        elif sum(check) == 1:
            ind = check.index(1)
            name = names[ind]
            st.error('You have added too much {}, please reduce the number of fields.'.format(name))
            df = df.iloc[:-1 , :]
            df.to_csv('app.csv')
        elif sum(check) == 2:
            ind1 = check.index(1)
            name1 = names[ind1]
            check[ind1] = 0
            ind2 = check.index(1)  
            name2 = names[ind2]
            st.error('You have added too much of {} and {}, please reduce the number of fields.'.format(name1,name2))
            df = df.iloc[:-1 , :]
            df.to_csv('app.csv')
        elif sum(check) == 3:
            ind1 = check.index(1)
            name1 = names[ind1]
            check[ind1] = 0
            ind2 = check.index(1)  
            name2 = names[ind2]
            check[ind2] = 0
            ind3 = check.index(1)  
            name3 = names[ind3]
            st.error('You have added too much of {}, {} and {}, please reduce the number of fields.'.format(name1,name2,name3))
            df = df.iloc[:-1 , :]
            df.to_csv('app.csv')
        elif sum(check) == 4:
            ind1 = check.index(1)
            name1 = names[ind1]
            check[ind1] = 0
            ind2 = check.index(1)  
            name2 = names[ind2]
            check[ind2] = 0
            ind3 = check.index(1)  
            name3 = names[ind3]
            check[ind3] = 0
            ind4 = check.index(1)  
            name4 = names[ind4]
            st.error('You have added too much of {}, {}, {} and {}, please reduce the number of fields.'.format(name1,name2,name3,name4))
            df = df.iloc[:-1 , :]
            df.to_csv('app.csv')

        # # if statements for crop characteristics
        # elif sum(check_char) == 1:
        #     ind = check_char.index(1)
        #     name = names_char[ind]
        #     st.error('The value of the {} is out of bounds. Please change the crop sequence'.format(name))
        #     df = df.iloc[:-1 , :]
        #     df.to_csv('app.csv')
        # elif sum(check_char) == 2:
        #     ind1 = check_char.index(1)
        #     name1 = names_char[ind1]
        #     check_char[ind1] = 0
        #     ind2 = check_char.index(1)  
        #     name2 = names_char[ind2]
        #     st.error('The values of the {} and the {} are out of bounds. Please change the crop sequence'.format(name1,name2))
        #     df = df.iloc[:-1 , :]
        #     df.to_csv('app.csv')
        # elif sum(check_char) == 3:
        #     ind1 = check_char.index(1)
        #     name1 = names_char[ind1]
        #     check_char[ind1] = 0
        #     ind2 = check_char.index(1)  
        #     name2 = names_char[ind2]
        #     check_char[ind2] = 0
        #     ind3 = check_char.index(1)  
        #     name3 = names_char[ind3]
        #     st.error('The values of the {}, the {} and the {} are out of bounds. Please change the crop sequence'.format(name1,name2,name3))
        #     df = df.iloc[:-1 , :]
        #     df.to_csv('app.csv')

        # # if statement for UL
        # elif sum(check_UL) > 0:
        #     st.error('The upper limit for the nutrient has been exceeded. Please  consider a new solution')
        #     df = df.iloc[:-1 , :]
        #     df.to_csv('app.csv')

# global calculations 
seqs = f.DefineSequenceNumber(df, df_CS)
fields = df['nb Fields'].values

NY_total, CY_total = f.getYield(seqs, fields, NY, CY)

percentages_NY, theta = f.getPercentages(NY_total, RNI)

percentages_NY_minerals = np.min(percentages_NY[6:15])
percentages_NY_vitamins = np.min(percentages_NY[15:24])
percentages_NY = np.append(percentages_NY[0:6], percentages_NY_minerals)
percentages_NY = np.append(percentages_NY,percentages_NY_vitamins)

CY_food_groups = f.DefineCropYield(CY_total)


if page == 'Guideline':
    st.markdown("<h1 style='text-align: center;'>Guideline</h1>", unsafe_allow_html=True)
    st.markdown(f'''
    BLA di BLA BLA \\
    LET'S GO.\\
    OKAAAAAYY LETS GOOOO.
    ''')

if page == 'Game':
    st.markdown("<h1 style='text-align: center;'>Game Crop Rotation</h1>", unsafe_allow_html=True)

    df.style.set_table_styles(
        [{
            'selector': 'th',
            'props': [('background-color', 'yellow')] #90EE90
        }])

    st.dataframe(df)
    columns1,mid, columns2 = st.columns([8,1,2])

    with columns1:

        # # number of fields left
        # st.metric('Nb of fields left', "{}".format(maxFields-sum(fields)))


        # Group results
        fig = f.create_figure(names,CY_food_groups)
        st.write(fig)

        # Cover - Structure - N need
        if df['Cover'].empty:
            df1 = pd.DataFrame(columns=['metric', 'value'])
            df1 = df1.append({'metric' : 'mean cover', 'value' : None}, ignore_index=True)
            df1 = df1.append({'metric' : 'mean structure', 'value' : None}, ignore_index=True)
            df1 = df1.append({'metric' : 'mean N need', 'value' : None}, ignore_index=True)
            st.dataframe(df1)
        else:
            df1 = pd.DataFrame(columns=['metric', 'value'])
            df1 = df1.append({'metric' : 'mean cover', 'value' : df['Cover'].values.mean()}, ignore_index=True)
            df1 = df1.append({'metric' : 'mean structure', 'value' : df['Structure'].values.mean()}, ignore_index=True)
            df1 = df1.append({'metric' : 'mean N need', 'value' : df['N need'].values.mean()}, ignore_index=True)
            st.dataframe(df1)

    with columns2:
        # progress bar optimal solution
        progressie = np.min(percentages_NY)/opt_value
        columns2.write('Progression: {}%'.format(np.around(100*progressie, 1)))
        columns2.progress(progressie)

        columns2.metric(Nutrients_list[0], "{}%".format(round(percentages_NY[0],1)))
        columns2.metric(Nutrients_list[1], "{}%".format(round(percentages_NY[1],1)))
        columns2.metric(Nutrients_list[2], "{}%".format(round(percentages_NY[2],1)))
        columns2.metric(Nutrients_list[3], "{}%".format(round(percentages_NY[3],1)))
        columns2.metric(Nutrients_list[4], "{}%".format(round(percentages_NY[4],1)))
        columns2.metric(Nutrients_list[5], "{}%".format(round(percentages_NY[5],1)))
        columns2.metric("Minerals", "{}%".format(round(percentages_NY[6],1)))
        columns2.metric("Vitamins", "{}%".format(round(percentages_NY[7],1)))

if page == 'Data':
    st.markdown("<h1 style='text-align: center;'>Data</h1>", unsafe_allow_html=True)
    st.dataframe(crop_char_sep)