# -*- coding: cp1250 -*-
#
# Egzamin z przedmiotu pozyskiwianie i przetwarzanie geodanych II
# Iga Gorczyca

import arcpy
from math import sqrt, atan, acos, cos, sin, pi

arcpy.env.overwriteOutput = True

#Słowniki

def read(geometry):
    try:
        lista = []
        i = 0
        for part in geometry:
            for pnt in part:
                if pnt:
                    lista.append([pnt.X, pnt.Y])
        i += 1
        return lista
    finally:
        del(i, part, pnt, geometry, lista)

#założenie 1: Analizie podlegają tylko wierzchołki dla którego ramiona tworzą kąt od
#180 +/- tolerancja (tolerancja jako parametr narżedzia wprowadzana przez użytkownika)

def az(p,q):
    try:
        dy = q[1]-p[1]
        dx = q[0]-p[0]
        if dx == 0:
            czwartak = 0
            if dy>0:
                azimuth=100
            if dy<0:
                azimuth=300                
        else:
            czwartak=atan(float(abs(dy))/float(abs(dx)))
            czwartak=czwartak*200/math.pi
            if dx>0:
                if dy>0:
                    azimuth = czwartak
                if dy<0:
                    azimuth = 400 - czwartak
                if dy==0:
                    azimuth = 0
            if dx<0:
                if dy>0:
                    azimuth = 200 - czwartak
                if dy<0:
                    azimuth = 200 + czwartak
                if dy==0:
                    azimuth = 200
        return azimuth
    except Exception, err:
        arcpy.AddError("blad azymut")
        arcpy.AddError(sys.exc_traceback.tb_lineno)
        arcpy.AddError(err.message)
    finally:
        del(dx,dy,czwartak)

        
def angle(azimuth1,azimuth2):
    angle = azimuth2 - azimuth1
    return(angle)


def clear_list(list1):
    unnecessary = []
    for i1 in range(len(list1)):
        
        prior = i1-1
        nextt = i1+1
        
        if prior == -1:
            prior = len(list1)-2

        if nextt > len(list1)-1:
            nextt = 1
            
        angle1=abs(angle(az(list1[i1],list1[prior]),az(list1[i1],list1[nextt])))
        
        if (angle1>(200-tolerancja) and angle1<(200+tolerancja)):
            unnecessary.append(i1)

    if len(unnecessary) == 0:
        return(list1)
    else:   
        unnecessary.reverse()
           
        for index in unnecessary:
            list1.pop(index)

        if unnecessary[-1] == 0: list1.append(list1[0])

        return(list1)

#Założenie 2,3,4: Sieczna powinna odcinać k wierzchołków obiektu – parametr narzędzia
                #Sieczna nie może przecinać obiektu
                #Sieczna może być zewnętrzną

def create_diagonal(list1):
    polygon = create_arcpy_polygon(list1)
    length1 = len(list1)-1
    list_diagonal = []
    for i1 in range(len(list1)-1):
        for i2 in range(i1+2,len(list1)-1):
                        
            if (((compute_range(length1,i1,i2) == k) and ((length1 - compute_range(length1,i1,i2)) >= k2)) or ((compute_range(length1,i2,i1) == k) and ((length1 - compute_range(length1,i2,i1)) >= k2))):
              
                if not create_arcpy_line([list1[i1],list1[i2]]).crosses(polygon):
                    list_diagonal.append([length(list1[i1],list1[i2]),i1,i2])         
        return(list_diagonal)

# Założenia 5,6:Iteracja przebiega do póki nie zostaną k2 punkty
#Iteracja postępuje od najkrótszej siecznej

def length(a,b):
    length = sqrt((a[1]-b[1])**2+(a[0]-b[0])**2)
    return(length)

def compute_range(length_of_list,x1,x2):
    if x2 - x1 < 0:
        output_range = length_of_list - x1 - 1 + x2
    else:
        output_range = x2 - x1 - 1
    return(output_range)

def search_min_diagonal(lista):
    minimum = lista
    for diagonal in lista:
        if diagonal[0] < minimum[0]:
            minimum = diagonal     
    return(minimum)

def delete_points(lista):
    shortest = search_min_diagonal(create_diagonal(lista))
    object1 = range(shortest[1],shortest[2]+1)+[shortest[1]]
    object1_1 = [lista[index] for index in object1]
    object2 = range(shortest[2],len(lista)-1)+range(0,shortest[1]+1)+[shortest[2]]
    object2_2 = [lista[index] for index in object2]

    if create_arcpy_polygon(object2_2).area > create_arcpy_polygon(object1_1).area:
        shortoff = object1_1
        main = object2_2
    else:
        shortoff = object2_2
        main = object1_1
    return([main,shortoff,shortest])


def generalization(building):
    
    ID = building[1]
    building = building[0]
    w = len(building)-1
    nr_shortoff = 1
    list_shortoff = []
    
  
    if not len(create_diagonal(building)) == 0:      
        while w > k2:
            building = clear_list(building)
            temp_building = building
            
            w = len(building)-1

            if not len(create_diagonal(building)) == 0:
                if w > k2:
                        building,shortoff,diagonal = delete_points(building)[0],delete_points(building)[1],delete_points(building)[2]
                        if create_arcpy_line([temp_building[diagonal[1]],temp_building[diagonal[2]]]).within(create_arcpy_polygon(temp_building)):    
                            shortoff = [shortoff,nr_shortoff,1]
                        else:
                            shortoff = [shortoff,nr_shortoff,0]
                            list_shortoff.append(shortoff)
                        nr_shortoff = nr_shortoff + 1
            else:
                break
            w = len(building)-1

    building = [building,ID]
    list_shortoff = [list_shortoff,ID]
    return(building,list_shortoff)


def create_arcpy_line(line):
    arcpy_line = arcpy.Polyline(arcpy.Array([arcpy.Point(line[0][0],line[0][1]),arcpy.Point(line[1][0],line[1][1])]))
    return(arcpy_line)

def create_arcpy_polygon(polygon):
    arcpy_polygon = arcpy.Polygon(arcpy.Array([arcpy.Point(ppoint[0],ppoint[1]) for ppoint in polygon]))
    return(arcpy_polygon) 


#PODANIE PARAMETRÓW
#tolerancja odchyłki kąta [grady]
tolerancja = 10
#ilosc odcinanych wierzcholkow
k=1
#ilosc punktow w wyniku:
k2=4
#nazwa pola z ID
field = 'id'
#ścieżka do folderu
s=r'C:\Users\gusia\Desktop\ppg2 egzamin'
#ścieżka do warstwy shapefile
shape = r'C:\Users\gusia\Desktop\ppg2 egzamin\dane2.shp'


cursor_read = arcpy.da.SearchCursor(shape, ['SHAPE@', field])
list_building = []
list_wrong = []
for row_read in cursor_read:
    try:
        geometry = read(row_read[0])
        list2 = [geometry,row_read[1]]
        list_building.append(list2)
    except:
        list_wrong.append(row_read[1])

result_list = []
result_list_shortoff = []
for polygon in list_building:
    try:
        result_list.append(generalization(polygon)[0])
        result_list_shortoff.append(generalization(polygon)[1])
    except:
        list_wrong.append(polygon[1])

result_shp = arcpy.CreateFeatureclass_management(s,'test_result.shp','POLYGON',shape)
result_shp_shortoff = arcpy.CreateFeatureclass_management(s,'test_result_shortoff.shp','POLYGON')
arcpy.AddField_management(result_shp_shortoff,'id_build','SHORT')
arcpy.AddField_management(result_shp_shortoff,'id_short','SHORT')
arcpy.AddField_management(result_shp_shortoff,'In_Out','SHORT')

with arcpy.da.InsertCursor(result_shp, ['SHAPE@', field]) as cursor:
    for polygon in result_list:
        cursor.insertRow([polygon[0],polygon[1]])

with arcpy.da.InsertCursor(result_shp_shortoff, ['SHAPE@', 'id_build', 'id_short','In_Out']) as cursor:
    for building in result_list_shortoff:
        for shortoff in building[0]:
            id_build = building[1]
            cursor.insertRow([shortoff[0],id_build,shortoff[1],shortoff[2]])

print('gotowe')


