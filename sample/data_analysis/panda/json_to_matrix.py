import sys
import pymongo
import pandas as pd

docs = [
{
    "Name":"John",
    "Age":29,
    "Gender":0,
    "Weight":60,
    "Score":80,
},
{
    "Name":"Mary",
    "Age":21,
    "Gender":1,
    "Weight":40,
    "Score":90,
},
{
    "Name":"Carter",
    "Age":30,
    "Gender":0,
    "Weight":70,
    "Score":50,
},
]

lst = list()

# index keyword: convert field to ordered index 0,1,2,3 ... 
for i in docs:
    s = pd.Series(i, index=["Age","Name", "Gender", "Weight", "Score"])
    lst.append(s)
    print "Series from json:\n{}".format(s)




# make M (Number of docs) x N (NUmber of keys ) matrix 
df = pd.DataFrame(lst)
print "DataFrame from Series:\n{}\n=========".format(df)
#print "df 0={}\n========".format(df.loc[0])
#print "df 0 cells={},{},{},{}\n=========".format(df.loc[0][0], df.loc[0][1], df.loc[0][2], df.loc[0][3])

'''
idx

    Age   Name  Gender  Weight  Score
0   29    John       0      60     80
1   21    Mary       1      40     90
2   30  Carter       0      70     50

'''

print "Age mean:{}, Weight mean:{}, Age std:{}, Age median:{}, Score median:{}".format(
        df['Age'].mean(), df['Weight'].mean(), df['Age'].std(), df['Age'].median(), df['Score'].median())

df.to_csv('out.csv',  sep=',', encoding='utf-8', index=False) # index: do not write index 0,1,2... as a new column

x = pd.read_csv('./out.csv')
print "DataFrame From csv file:\n{}\n=========".format(x)

