
# coding: utf-8

# In[43]:

from bs4 import BeautifulSoup
import urllib2
import sys
import pandas as pd
import html5lib
reload(sys)  
sys.setdefaultencoding('UTF8')



def PopulateAccessoriesFile(AccessoriesLink,entries,AccessoriesFile):
    if len(AccessoriesLink)<4:
        print "No Accessories for this car"

        return 
    OptionPage=urllib2.urlopen(AccessoriesLink).read()
    soup3=BeautifulSoup(OptionPage)
    Types=soup3.findAll('div',attrs={'class':'accessory-category' })
    print "Populating AccessoryFile",
    for t in Types:
        subcategory=str(t.attrs['id'][3:])
        f=t.find('div',attrs={'class':'l-center-align accessory-category__button'})
        if f!=None:
            accesspage="http://www.suzuki.com.au/"+str(f.find('a').attrs['href'])
            accesspage=urllib2.urlopen(accesspage).read()
            soup4=BeautifulSoup(accesspage)
            Allaccessory=soup4.findAll('div',attrs={'class':'tile__inner tile--arrow-up'})
        else:
            Allaccessory=t.findAll('div',attrs={'class':'tile__inner tile--arrow-up'})
        for every in Allaccessory:
            accessory=every
            Aname=str(accessory.find('h3').text)
            details=accessory.find_all('p')
            det=[]
            for each in details:
                det.append(each.text)
            temp=[]
            for each in det:
                each=each.strip().split("\n")
                temp.append(each)   
            Apartnumber=str(temp[0][1]).strip()
            Aavailableon=str(temp[1][1]).strip()
            try:
                Adescription=str(temp[2][0]).strip()
            except:
                Adescription="NA"

            details=[subcategory,Aname,Apartnumber,Adescription,Aavailableon]
            entry=entries+details
            insert=[entry[0],entry[3]," ","GENUINE_ACCESSORY",entry[6],entry[4],entry[5],entry[7],entry[8]," "," "," "]
            #['BrandName','Category','Style','Family','TypeOfAccessory','Name','PartNumber','Description','AvailableOn']

            
            AccessoriesData=pd.read_csv(AccessoriesFile)
            row=pd.DataFrame([insert],columns=['make','family','modelFactoryCode','optionType','code','category','title','description','comments','estimatedFitmentTime','rrp','imageUrls'])
            AccessoriesData=AccessoriesData.append(row)
            AccessoriesData.to_csv(AccessoriesFile,index=False)
            print ".",
            
            
def PopulateOverViewFile(OverViewLink,entries,OverViewFile):
    OptionPage=urllib2.urlopen(OverViewLink).read()
    soup2=BeautifulSoup(OptionPage)
    #Finding summary
    Summarydetails=soup2.findAll('h3',attrs={'class':'model-specs-summary__value' })
    Description=[]
    for i in Summarydetails:
        Description.append(str(i.text.strip()))
    Description=list(set(Description))
    #Finall variants with color and pic links
    Variantdetails=soup2.findAll('div',attrs={'class':'model-spin__variant'})
    print "Populating OverviewFile",
    for each in Variantdetails:
        v=each
        vname=str(v.attrs['data-modelspin-variant'])
        vname=vname.split(" ")
        vname=" ".join(vname)
        vname=vname.capitalize()
        colornames=each.find_all('ul' ,attrs={'class':'model-spin__gallery'})
        itscolors=[]
        for every in colornames:
            fc=every
            fc=fc.attrs['data-colour']
            fc=fc.split("_")
            fc=" ".join(fc)
            fc=fc.capitalize()

            piclink=every.find('li',attrs={'class':'model-spin__gallery__item'})
            plink=piclink.find('div',attrs={'class':'bg-image bg-image-default'})
            picurl=plink.attrs['style']
            picurl=picurl.split(" ")[1][5:len(picurl.split(" ")[1])-1:]
            picurl="http://www.suzuki.com.au/"+picurl

            details=[Description,vname,fc,picurl]
            entry=entries+details
            insert=[entry[0],entry[3]," ","BODY_COLOUR"," ",entry[2],entry[5],entry[6],entry[4]," "," ",entry[7]]
            
            #['BrandName','Category','Style','Family','Description','Variant','Color','ImageLink']
            OverViewData=pd.read_csv(OverViewFile)
            row=pd.DataFrame([insert],columns=['make','family','modelFactoryCode','optionType','code','category','title','description','comments','estimatedFitmentTime','rrp','imageUrls'])
            OverViewData=OverViewData.append(row)
            OverViewData.to_csv(OverViewFile,index=False)
            print ".",
            
def PopulateSpecificationFile(SpecificationsLink,entry,SpecificationsFile,SpecificationsCols):
    df=pd.read_html(SpecificationsLink,attrs={'class':'responsive model-specifications__table'})
    
    temp=df[0]
    temp.drop(temp.index,inplace=True)
    for each in range(0,len(df)):
        temp=temp.append(df[each],ignore_index=True)

    x=temp.columns.values
    indexes=[]
    for each in x:
        s=str(each.strip(' \t\n\r'))
        s= s.replace('\n', '')
        s=s.split(" ")
        s=" ".join(s)
        indexes.append(s)
    indexes=indexes[1:len(indexes)-1]
    indexes

    trans=temp.transpose()
    index=range(0,len(temp.columns))
    temp.columns=index
    newColNames=temp[0]
    trans.index=index
    indextoDrop=[0,len(index)-1]
    trans=trans.drop(trans.index[indextoDrop])
    trans.columns=newColNames
    trans.index=range(0,len(trans))
    print "Populating Specifications File..",
    #return trans
    cols=range(0,155)
    SpecificationsData=pd.DataFrame(columns=cols)
    
    for i,x in trans.iterrows():
        initials=['',indexes[i],'','','','','',entry[0],entry[3],indexes[i],'',entry[1],entry[2]]
        col=list(x)
        insert=initials+col
        row=pd.DataFrame([insert],columns=cols)
        #return row
        SpecificationsData=SpecificationsData.append(row,ignore_index=True)
        #SpecificationsData.to_csv(SpecificationsFile,index=False)
        print ".",
    SpecificationsData.columns=SpecificationsCols
    
    import os.path 
    if os.path.exists(SpecificationsFile):
        OriginalData=pd.read_csv(SpecificationsFile)
        od=pd.DataFrame(columns=cols)
        for i,x in OriginalData.iterrows():
            insert=list(x)
            row=pd.DataFrame([insert],columns=cols)
            od=od.append(row,ignore_index=True)
        
        od.index=range(0,len(od))
        od.columns=SpecificationsCols
        SpecificationsData=SpecificationsData.append(od,ignore_index=True)
        
        
    SpecificationsData.to_csv(SpecificationsFile,index=False)
    




if __name__ == "__main__":
    url=str(sys.argv[1])
    #url="http://www.suzuki.com.au/vehicles"
    OverViewFile="C:\Users\ysaxe2\Desktop\SuzukiAUScraper\suzuki-options.csv"
    AccessoriesFile="C:\Users\ysaxe2\Desktop\SuzukiAUScraper\suzuki-options.csv"
    SpecificationFile="C:\Users\ysaxe2\Desktop\SuzukiAUScraper\suzuki-models.csv"
    SpecificationCols=['factoryCode',
     'variantCode',
     'marketingModelCode',
     'glassCode',
     'glassNvic',
     'franchiseCode',
     'makeCode',
     'make',
     'family',
     'variant',
     'series',
     'modelCategory',
     'style',
     'Enginetype',
     'Displacementcm3',
     'Cylinders',
     'Valves',
     'Borexstrokemm',
     'Compressionratio',
     'Variablevalvetimingcamshaft',
     'MaximumpowerkW@rpm',
     'MaximumtorqueNm@rpm',
     'ManualTransmission',
     'Type',
     'Paddleshifters',
     '1stgearratio',
     '2ndgearratio',
     '3rdgearratio',
     '4thgearratio',
     '5thgearratio',
     '6thgearratio',
     'Reversegearratio',
     'Finaldriveratio',
     'All-wheeldrive',
     '4-wheel-drive',
     'AutomaticTransmission',
     'Type',
     'Paddleshifters',
     'GearRatio',
     '1stgearratio',
     '2ndgearratio',
     '3rdgearratio',
     '4thgearratio',
     '5thgearratio',
     '6thgearratio',
     'Reversegearratio',
     'Finaldriveratio',
     'All-wheeldrive',
     '4-wheel-drive',
     'Fuel',
     'nan',
     'nan',
     'FuelTankCapacityL',
     'Consumption*L100kmmanual',
     'Consumption*L100kmautomatic',
     'CO2emissionsgkmmanual',
     'CO2emissionsgkmautomatic',
     'Steering',
     'Brakes',
     'Front',
     'Rear',
     'Suspension',
     'Front',
     'Rear',
     'Tyres&Wheels',
     'Tyreswidthprofile',
     'Wheelsize',
     'Wheeltype',
     'Sparewheel',
     'Weights',
     'Kerbweight,minimumkgManual',
     'Kerbweight,minimumkgAutomatic',
     'Grossvehicleweightkg',
     'TowingCapacity',
     'Brakedkg',
     'Unbrakedkg',
     'Ballweightkg',
     'Immobiliser',
     'Anti-theftalarm',
     'Frontairbags',
     'Sideairbags',
     'Curtainairbags',
     'Kneeairbagdriver',
     'Anti-lockbrakingsystemABS',
     'ElectronicbrakeforcedistributionEBD',
     'BrakeassistsystemBAS',
     'VehiclestabilitycontrolESP\xc2\xae^',
     'Tractioncontrol',
     'Frontseatbelts',
     'Rearseatbelts',
     'Childseatanchoragepoints',
     'HillholdcontrolManual',
     'HillholdcontrolAutomatic',
     'Hilldescentcontrol',
     'Steeringwheel',
     'Columnadjustment',
     'Cruisecontrol',
     'Powerwindows',
     'Powerdoorlocks',
     'Remotecontrolled',
     'KeylessEntryandStartSystem',
     'Airconditioning',
     'Pollenfilter',
     'Rearviewmirrorautodimming',
     'Informationdisplay',
     'Digitalclock',
     'Outsidetemperaturegauge',
     'Fuelconsumptiongaugeinstantaneousaverage',
     'Drivingrange',
     'GearpositionindicatorManual',
     'GearpositionindicatorAutomatic',
     'Seatupholstery',
     'Frontseatheightadjustment',
     'Powerseatdriver',
     'Powerseatfrontpassenger',
     'Lumbaradjust',
     'Rearseats',
     'Headrests',
     'Frontmaplight',
     'Frontcabinlight',
     'Centrecabinlight',
     'Bootlight',
     'Luggagearealight',
     'Cupholders',
     'Bottleholders',
     '12vpoweroutlet',
     'Luggageareacover',
     'Luggageboard',
     'Satellitenavigation',
     'Livetrafficupdates',
     'Touchscreen',
     'Voicecommand',
     'CDplayer',
     'MP3capable',
     'Steeringwheelcontrols',
     'Externaldevicesconnectivity',
     'Speakersnumberof',
     'Bluetooth\xc2\xaeconnectivity',
     'Headlights',
     'Withdusksensor',
     'Frontfoglights',
     'Doormirrors',
     'Doormirrors-finish',
     'Builtinturningindicatorlights',
     'Doorhandles-finish',
     'Sportsbodykit',
     'Rearwindowwasherandwiper',
     'Rearwindowwiper',
     'Windshieldwiperswithrainsensor',
     'Parkingsensors',
     'ReversingCamera',
     'Bootspoiler',
     'Roofspoiler',
     'Sunroof',
     'Roofrails']
    page = urllib2.urlopen(url).read()
    soup=BeautifulSoup(page)
    data = soup.findAll('div',attrs={'class':'model-tile__inner'});
    Options=[]
    for i in data:
        Options.append("http://www.suzuki.com.au/" + i.a['href']);
    for car in Options:
        temp=car
        temp=temp.split("/")
        BrandName="Suzuki"
        Category="Vehicles"
        Style=str(temp[len(temp)-2]).capitalize()
        Family=str(temp[len(temp)-1]).capitalize()
        OptionPage=urllib2.urlopen(car).read()
        soup2=BeautifulSoup(OptionPage)
        navlinks=soup2.find('div',attrs={'class':'suzuki-vehicle-nav'})
        alllinks=navlinks.find('ul',attrs={'class':'unstyled suzuki-vehicle-nav__menu__items'})

        alllinks=alllinks.findAll('a')
        links=[]
        for each in alllinks:
            links.append(each.attrs['href'])

        base="http://www.suzuki.com.au"
        OverViewLink=base+links[0]
        SpecificationLink=base+links[1]


        try:
            AccessoriesLink=base+links[3]
        except:
            AccessoriesLink="NA"

        #acc.append(SpecificationLink)

        entries=[BrandName,Category,Style,Family]
        ##PopulateOverviewFile
        PopulateOverViewFile(OverViewLink,entries,OverViewFile)

        #PopulateSpecificationFile
        PopulateSpecificationFile(SpecificationLink,entries,SpecificationFile,SpecificationCols)

        #PopulateAccessoriesFile
        PopulateAccessoriesFile(AccessoriesLink,entries,AccessoriesFile)
        
    
    


# In[ ]:



