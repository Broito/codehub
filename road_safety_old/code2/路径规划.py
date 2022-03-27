#给定起终点A（x1,y1），B(x2,y2)
def getxianglin(a):

    return s #数组[point dis risk]
close = [] #存储遍历过的节点
def ASTAR(start,end):
    open = [start] #存储未遍历的节点
    x1 = start[0]
    y1 = start[1]
    x2 = end[0]
    y2 = end[1]
    s = getxianglin(start)
    open.extend(s[0])
    score = []
    for t in s:
        h = t[1]/2*risk #实际代价
        g = abs(t[0][0]-start[0])+abs(t[0][1]-start[1]) #估计代价
        f = h+g
        score.append([t,f])
    sorted(score, key=lambda a_list: a_list[1])
    close.append(score[-1][0])
    start = score[-1][0]
    if start=end:
        return close
    else:
        ASTAR(start,end)

'''
  2: while (Open表非空)  {    
  3:   从Open中取得一个节点X，并从OPEN表中删除。   
  4:   if (X是目标节点)   {     
  5:     求得路径PATH；   
  6:     返回路径PATH；   
  7:   }    
  8:   for (每一个X的子节点Y)   {     
  9:     if (Y不在OPEN表和CLOSE表中)    {      
 10:       求Y的估价值；     
 11:       并将Y插入OPEN表中；    
 12:     }else if (Y在OPEN表中)    {      
 13:       if (Y的估价值小于OPEN表的估价值)      
 14:         更新OPEN表中的估价值；    
 15:       }    
 16:     else {//Y在CLOSE表中          
 17:       if (Y的估价值小于CLOSE表的估价值)     {       
 18:         更新CLOSE表中的估价值；       
 19:         从CLOSE表中移出节点，并放入OPEN表中；    
 20:       }    
 21:     }  
 22:   }
 23:   将X节点插入CLOSE表中；     
 24:   按照估价值将OPEN表中的节点排序；
 25: }
'''

