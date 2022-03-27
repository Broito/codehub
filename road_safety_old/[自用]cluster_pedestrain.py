import arcpy,datetime,math,xlwt
from arcpy import env

env.workspace = r"E:\FloatVehicle2019\cluster.mdb"
workbook = xlwt.Workbook()
sheet = workbook.add_sheet("clusteraltime")
sheet.write(0, 0, "newoid")
# acciFiled=[]#center_road �и�ʱ����¹����ֶ�,��12��
# col=1
# for i in range(0,24,2):
#     den="density%d_%d"%(i,i+2)
#     sheet.write(0,col, den)
#     acci="acci%d_%d"%(i,i+2)
#     acciFiled.append(acci)
#     col+=1
sheet.write(0,1,'density_pedestrain')
# sheet.write(0,1,'density9_10')
# sheet.write(0,1,'density17_18')
# sheet.write(0,1,'density18_19')
rowID=1
searchFiled= ["ToCumul_Length","newoid"]
# searchFiled.extend(['acci8_9','acci9_10','acci17_18','acci18_19'])
# acciFiled = ['acci8_9','acci9_10','acci17_18','acci18_19']
searchFiled.extend(['pedestrain'])
acciFiled = ['pedestrain']

arcpy.CheckOutExtension("Network")
networkND = "network\\network_ND"#�������ݼ�
centerRoad = "center_road_pedestrain"#���ĵ�����
seardis = 300 #��ʵ�������뾶
bandWidth = "300"  # �ڷ����������85�������뾶�൱��100��
curCenter = sorted(arcpy.da.SearchCursor(centerRoad, ["SHAPE@", "newoid"],"""[newoid] >1952 AND [newoid]<2300"""), key=lambda a_list: a_list[1])  # ������·���ĵ�����
for point in curCenter:
    try:
        facility=point[0]
        #outLine = "outline%d"%(point[1])  #�������
        serviceName = "serviceN%d"%(point[1])  # ����������
        Lines = "%s\\Lines" % (serviceName)  # �������������ͼ��
        join_line_point="join_line_point%d"%(point[1])#·�ߺ����ĵ���������ݣ������һ��������
        arcpy.MakeServiceAreaLayer_na(networkND, serviceName, "Length", "TRAVEL_FROM", bandWidth, "NO_POLYS", "NO_MERGE", "RINGS","TRUE_LINES", "NON_OVERLAP", "NO_SPLIT", "", "", "ALLOW_UTURNS", "", "NO_TRIM_POLYS","", "NO_LINES_SOURCE_FIELDS", "NO_HIERARCHY", "")
        arcpy.AddLocations_na(serviceName, "Facilities", facility, "", "")
        arcpy.Solve_na(serviceName, "SKIP", "TERMINATE", "")
        #arcpy.CopyFeatures_management(Lines, outLine, "", "0", "0", "0")
        arcpy.SpatialJoin_analysis(Lines, centerRoad, join_line_point)
        curJoin = sorted(arcpy.da.SearchCursor(join_line_point, searchFiled,""""newoid" IS NOT null"""))
        if len(curJoin)!=0:
            sheet.write(rowID, 0, point[1])  # д��newoid
            for yearNum in range(len(acciFiled)):#ִ��ʱ��Σ���4��
                sumKernel = 0 # ��ǰ����ܶ�ֵ
                nowID = 0  # ���ڼ�¼��ǰ���Ƿ����¹���
                for row in curJoin:
                    dis = float(math.pow(row[0], 2)) / (2 * math.pow(seardis, 2))  # ʹ�ø�˹�ܶȺ���
                    if row[1]== point[1] and nowID==1:#��ʾ��ǰ�¹��Ѿ������
                        continue
                    if  row[1]== point[1] :  # ˵����ǰ�����¹���������������������¼��ֻʹ��һ�������Ҿ��벻��ʹ��ToCumul_Length��Ӧ��Ϊ0,
                        dis=0
                        nowID=1
                    kernel=(1.0/math.sqrt(2*math.pi))*math.exp(-dis)#��ǰ���һ���ܶ�ֵ
                    acci_num = row[2+yearNum]
                    if acci_num == None:
                        acci_num = 0                
                    kernel=kernel*acci_num#�ж����¹ʵ�ͼ�����ٴ�
                    sumKernel+=kernel
                sumKernel=sumKernel/seardis *1000 #���������뾶,�ܶ�ֵΪÿǧ��
                colID=1+yearNum
                sheet.write(rowID, colID, sumKernel)  # д���ܶ�
        rowID+=1
        arcpy.Delete_management(serviceName, "")#ɾ����ʱ�ķ���ͼ��
        arcpy.Delete_management(join_line_point)  # ɾ����ʱ����
        del curJoin
        print point[1]
        workbook.save(r"E:\FloatVehicle2019\speed_distribution\200m_result\200m_pedestrain_NKDE\cluster_pedestrain_300.xls")  # ��������
    except:
        print point[1],"data_wrong"#��ǰ��û�л��ֵ
del curCenter
