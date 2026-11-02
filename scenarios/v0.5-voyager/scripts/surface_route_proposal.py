"""Bounded geometry-only route proposal; never terrain/Native path clearance.

Core-building build bounds are conservative proposals, not walking footprints.
Fresh public terrain/Move checks and actual terminal progress remain required.
"""
import heapq
import math


def dot(a,b): return sum(x*y for x,y in zip(a,b))
def unit(a):
    n=math.sqrt(dot(a,a))
    if n<=0: raise ValueError('invalid surface vector')
    return tuple(x/n for x in a)
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


class Projection:
    def __init__(self,start):
        self.radius=math.sqrt(dot(start,start));self.normal=unit(start)
        axis=min(((1,0,0),(0,1,0),(0,0,1)),key=lambda x:abs(dot(self.normal,x)))
        self.u=unit(cross(self.normal,axis));self.v=cross(self.normal,self.u)
    def project(self,p):
        p=unit(p);den=dot(p,self.normal)
        if den<.3: raise ValueError('proposal exceeds bounded local hemisphere')
        return self.radius*dot(p,self.u)/den,self.radius*dot(p,self.v)/den
    def surface(self,p):
        q=unit(tuple(self.normal[i]+self.u[i]*p[0]/self.radius+self.v[i]*p[1]/self.radius for i in range(3)))
        return tuple(x*self.radius for x in q)


def route(goal,rectangles,cell=2.0,goal_radius=45.0):
    """Return planar short waypoints to an interaction region, not its centre."""
    if len(rectangles)>512 or cell<1 or cell>4 or goal_radius<5 or goal_radius>60:
        raise ValueError('proposal bounds')
    gx,gy=goal;lo_x=math.floor((min(0,gx)-35)/cell);hi_x=math.ceil((max(0,gx)+35)/cell)
    lo_y=math.floor((min(0,gy)-35)/cell);hi_y=math.ceil((max(0,gy)+35)/cell)
    if (hi_x-lo_x+1)*(hi_y-lo_y+1)>20000: raise ValueError('proposal grid bound')
    if any(len(r)!=4 or r[0]>r[2] or r[1]>r[3]for r in rectangles):raise ValueError('invalid bounds')
    # A stable player can touch overlapping conservative build enclosures.
    # Do not erase those enclosures and route through a machine. Propose one
    # short outward step which never penetrates either enclosure more deeply.
    containing=[r for r in rectangles if r[0]<=0<=r[2]and r[1]<=0<=r[3]]
    obstacles=[r for r in rectangles if r not in containing]
    if containing:
        def depth(x,y,r):
            a,b,c,d=r
            return max(0,min(x-a,c-x,y-b,d-y)) if a<=x<=c and b<=y<=d else 0
        limits=[depth(0,0,r)for r in containing];escapes=[]
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            norm=math.hypot(dx,dy)
            for length in (8,10,12):
                x,y=dx*length/norm,dy*length/norm
                if any(r[0]-3<=x<=r[2]+3 and r[1]-3<=y<=r[3]+3 for r in containing):continue
                good=True
                for i in range(1,int(length*2)+1):
                    px,py=x*i/(length*2),y*i/(length*2)
                    if any(depth(px,py,r)>limit+1e-6 for r,limit in zip(containing,limits))or any(a<=px<=c and b<=py<=d for a,b,c,d in obstacles):
                        good=False;break
                if good:escapes.append((length+.1*math.hypot(x-gx,y-gy),(x,y)))
        if not escapes:raise ValueError('no bounded outward escape proposal')
        point=min(escapes,key=lambda x:x[0])[1]
        return dict(executable=False,terrainVerified=False,nativePathClearance=False,
                    escapeConservativeEnclosures=True,points=[point],examined=len(escapes))
    def blocked(x,y):return any(a<=x<=c and b<=y<=d for a,b,c,d in obstacles)
    start=(0,0);queue=[(0,0,start)];cost={start:0};parent={};found=None
    while queue:
        _,g,p=heapq.heappop(queue)
        if g!=cost.get(p):continue
        x,y=p[0]*cell,p[1]*cell
        if math.hypot(x-gx,y-gy)<=goal_radius and not blocked(x,y):found=p;break
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            q=(p[0]+dx,p[1]+dy);qx,qy=q[0]*cell,q[1]*cell
            if not(lo_x<=q[0]<=hi_x and lo_y<=q[1]<=hi_y)or blocked(qx,qy):continue
            if blocked((x+qx)/2,(y+qy)/2)or dx and dy and(blocked(x+dx*cell,y)or blocked(x,y+dy*cell)):continue
            ng=g+cell*math.hypot(dx,dy)
            if ng>=cost.get(q,math.inf):continue
            cost[q]=ng;parent[q]=p
            heapq.heappush(queue,(ng+max(0,math.hypot(qx-gx,qy-gy)-goal_radius),ng,q))
    if found is None:raise ValueError('no bounded proposal')
    path=[found]
    while path[-1]!=start:path.append(parent[path[-1]])
    path.reverse();points=[];last=path[0]
    for i,p in enumerate(path[1:],1):
        turn=i+1<len(path)and(p[0]-path[i-1][0],p[1]-path[i-1][1])!=(path[i+1][0]-p[0],path[i+1][1]-p[1])
        if math.hypot((p[0]-last[0])*cell,(p[1]-last[1])*cell)>=10 or turn or i==len(path)-1:
            points.append((p[0]*cell,p[1]*cell));last=p
    if not points:points=[(found[0]*cell,found[1]*cell)]
    return dict(executable=False,terrainVerified=False,nativePathClearance=False,points=points,examined=len(cost))
