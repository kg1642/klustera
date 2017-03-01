from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.db import connection
from .models import FbUsers, PageLikes
from django import forms
import os.path
import datetime
import csv


#probs_location, location, categories are in the format <('item',)>. This function makes them just <item> so that it does not create error when querying mysql
def trim_data(items_list):
    return_list=[]
    for item in items_list:
        s_item=item[0]
        return_list.append(s_item)
    return return_list

def form_validation(age_low, age_high, display_list):
    out=''
    if (age_low != ''):
        try:
            age_low = int(age_low)
        except ValueError:
            out=out+'Age should be a postive integer\n'
    if (age_high != ''):
        try:
            age_high = int(age_high)
        except ValueError:
            out = out + 'Age should be a postive integer\n'
    if (len(display_list)==0):
        out=out+'You should at least choose one field to display in Show section.'
    return out

def make_query_item(item_list):
    sql_query=''
    i=0
    for item in item_list:
        if (item=='unidentified'):
            item=''
        if (i == 1):
            sql_query = sql_query + ','
        sql_query = sql_query + "'" + str(item) + "'"
        i = 1
    sql_query = sql_query + ')'
    return (sql_query)


#the function creates mysql_query based on the paramteres given
def create_query_full(page_categories_list, gender_list, location_list, probs_location_list, age_low, age_high, display_list):
    query_middle1=''
    j=0
    #There are two tables. If page categories list is not empty we need to qeury both tables Fb_Users and Page_likes.
    if (len(page_categories_list)>0):
        query_start = 'select distinct(p.id_fb) as id_fb'
        query_middle2= 'from central.Fb_Users m, central.Page_likes p where m.id_fb=p.id_fb'
        query_middle2=query_middle2+' and p.category in ('+make_query_item(page_categories_list)
        j=1
    else:
        query_start= 'select distinct(m.id_fb) as id_fb'
        query_middle2=' from central.Fb_Users m where '
    for display in display_list:
        if (display!='id_fb'):
            query_middle1=query_middle1+', m.'+str(display)
        query_middle1=query_middle1+' '
    query_end=''
    if (len(gender_list)!=0):
        if (j==0):
            query_end=query_end+' m.gender in ('+make_query_item(gender_list)
            j=1
        else:
            query_end = query_end + ' and m.gender in (' + make_query_item(gender_list)
    if (len(location_list)!=0):
        if (j==1):
            query_end = query_end + ' and m.location in ('+make_query_item(location_list)
        else:
            query_end = query_end + ' m.location in ('+make_query_item(location_list)
            j=1
    if (len(probs_location_list) != 0):
        if (j == 1):
            query_end = query_end + ' and m.probs_location in (' + make_query_item(probs_location_list)
        else:
            query_end = query_end + ' m.probs_location in ('+make_query_item(probs_location_list)
            j = 1
    if (age_low != '' and age_high!=''):
        if ((int(age_low))>int(age_high)):
            temp=age_low
            age_low=age_high
            age_high=temp
    age_range_datetime=[]       #saving age range in datetime format
    if (age_low!=''):
        if (j == 1):
            query_end=query_end+' and m.age >= %s'
        else:
            query_end = query_end + ' m.age >=%S'
        age_range_low=datetime.datetime.now()-datetime.timedelta(days=365.25*(int(age_low)))
        age_range_datetime.append(age_range_low)

    if (age_high!=''):
        if (j == 1):
            query_end=query_end+' and m.age <= %s'
        else:
            query_end = query_end + ' m.age <= %s'
        age_range_high = datetime.datetime.now() - datetime.timedelta(days=365.25 * (int(age_high)))
        age_range_datetime.append(age_range_high)

    query_full=query_start+query_middle1+query_middle2+query_end+';'

    #if more than 1 page categories chosen then also display the page category name
    #print(query_full)
    return(query_full, display_list, age_range_datetime)


#changing age in years from datetime format
def age_in_years(datam, display_list):
    age_index = display_list.index('cumple')
    if datam[age_index] == '' or datam[age_index] == None:
        return('')
    else:
        return(datetime.datetime.now().year - datam[age_index].year)



def remove_duplicates(data):
    data=list(data)
    data_cleaned=[]
    i=0
    k=0
    while((i+k)<len(data)):
       data_cleaned.append(list(data[i]))
       id_fb = list(data[i])[0]
       for j in range(i + 1, len(data)):
            if (id_fb == list(data[j])[0]):
                data.remove(data[j])
                k=k+1
       i=i+1
    return (data_cleaned)

#this function queries the database based on the parameters given
def retrieve_data(page_categories_list, gender_list, location_list, probs_location_list, age_low, age_high, display_list):
    (query_full,display_list, age_range_datetime)=create_query_full(page_categories_list, gender_list, location_list, probs_location_list, age_low, age_high, display_list)
    cursor = connection.cursor()
    if (len(age_range_datetime)==0):
        cursor.execute(query_full)
    elif (len(age_range_datetime)==1):
        cursor.execute(query_full,(age_range_datetime[0]))
    elif (len(age_range_datetime)==2):
        cursor.execute(query_full,(age_range_datetime[0], age_range_datetime[1]))
    data = cursor.fetchall()
    global data_list
    data_list=[]
    global display_list_out
    display_list_out=display_list
    if (len(data)==0):
        return (data_list, display_list)
    data = remove_duplicates(data)  #removing duplicates from the data
    for datam in data:
        if not 'id_fb' in display_list:
            datam.pop(0)
        if 'cumple' in display_list:
            cumple_index = display_list.index('cumple')
            datam[cumple_index]= age_in_years(datam, display_list)
            #display_list[cumple_index]='age'
            #display_list_out[cumple_index]='age'
        data_list.append(datam)

    #replacing cumple with age for the output
    if 'cumple' in display_list:
        display_list[cumple_index]='age'
        display_list_out[cumple_index]='age'
    return (data_list, display_list)

def index(request):
    template=loader.get_template('filterdata/index.html')
    cursor = connection.cursor()
    #fetching page_categories, locations and probs_locationd from database
    cursor.execute('SELECT distinct(category) as category from Page_likes;')
    categories=trim_data(cursor.fetchall())
    cursor.execute('SELECT distinct(location) as location from Fb_Users;')
    locations=trim_data(cursor.fetchall())
    cursor.execute('SELECT distinct(probs_location) as probs_location from Fb_Users;')
    probs_locations = trim_data(cursor.fetchall())
    context={
        'categories':categories,
        'locations':locations,
        'probs_locations':probs_locations
    }
    #form=form()
    return HttpResponse(template.render(context, request))
    #return render(request, 'filterdata/index.html', {'form': form})


def datareturn(request):
    template = loader.get_template('filterdata/datareturn.html')
    if request.method=='POST':
        post_data=(request.POST)
        #print (post_data)
        page_categories_list=post_data.getlist('page_categories[]')
        gender_list=post_data.getlist('gender[]')
        location_list=post_data.getlist('locations[]')
        probs_location_list=post_data.getlist('probs_locations[]')
        age_low=post_data.get('age_low')
        age_high = post_data.get('age_high')
        display_list=post_data.getlist('display[]')
        check=form_validation(age_low, age_high, display_list)
        if (check==''):
            (data, display_list)=retrieve_data(page_categories_list, gender_list, location_list, probs_location_list, age_low, age_high, display_list)
            length=len(data)
            context={
                'data':data,
                'display_list': display_list,
                'length':length
            }
        else:
            return HttpResponse(check)
    #return HttpResponse("Success")
    return HttpResponse(template.render(context, request))


#for download button
#it outputs the results as csv
def download(request):
    if (request.method=='GET'):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data.csv"'

        writer = csv.writer(response)
        writer.writerow(display_list_out)
        writer.writerows(data_list)
        return response
