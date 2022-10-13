package personal.algors.jtstools
import com.vividsolutions.jts.geom.{Coordinate, Geometry, GeometryFactory, LineString, Point, Polygon}

import scala.math.{Pi, abs, atan, atan2, cos, sin, sqrt, acos, pow}
import scala.collection.mutable.ArrayBuffer
object OldJTSTools {
  private val geometryFactory = new GeometryFactory()
  val createPoint: (Double, Double) => Point = (x: Double, y: Double) => geometryFactory.createPoint(new Coordinate(x, y))
  val createLineString: (Array[Point]) => LineString = (points: Array[Point]) => geometryFactory.createLineString(points.map(x => x.getCoordinate))
  def createPoint(p: (Double, Double)): Point = {
    geometryFactory.createPoint(new Coordinate(p._1, p._2))
  }
  def createLineString(p: Point*): LineString = {
    val points = p.map(x => x.getCoordinate).toArray
    geometryFactory.createLineString(points)
  }

  def createPolygon(line: LineString, appendStartPoint: Boolean = true): Polygon = {
    appendStartPoint match {
      case true => {
        val points = new ArrayBuffer[Coordinate]()
        points.appendAll(line.getCoordinates)
        points.append(line.getStartPoint.getCoordinate)
        geometryFactory.createPolygon(points.toArray)
      }

      case false => {
        val points = new ArrayBuffer[Coordinate]()
        points.appendAll(line.getCoordinates)
        geometryFactory.createPolygon(points.toArray)
      }
    }
  }

  def createPolygon(points: Array[(Double, Double)]): Polygon = {
    this.createPolygon(this.createLineString(points.map(this.createPoint(_))))
  }

  def createNullPolygon: Polygon = {
    geometryFactory.createPolygon(Array(new Coordinate()))
  }

  def createNullPoint: Point = {
    geometryFactory.createPoint(new Coordinate())
  }

  // 非常重要，要注意点坐标表示是使用弧度还是角度制
  // 角度转弧度
  def angle2Rad(x: Double, y: Double): (Double, Double) = (x / 180 * Pi, y / 180 * Pi)

  def angle2Rad(p: Point): Point = createPoint(p.getX / 180 * Pi, p.getY / 180 * Pi)

  // 弧度转角度
  def rad2Angle(x: Double, y: Double): (Double, Double) = (x * 180 / Pi, y * 180 / Pi)

  def rad2Angle(p: Point): Point = createPoint(p.getX * 180 / Pi, p.getY * 180 / Pi)
  /**
   * 两点之间的距离（地球表面距离sphere、欧氏距离cartesian）米
   *
   * @param p1
   * @param p2
   * @param distanceType
   * @return
   */
  def distance2D(p1: Point, p2: Point, distanceType: String = "sphere", coordType: String = "angle"): Double = {
    distanceType match {
      case "sphere" => {
        val earthRadius = 6371393.0
        val p1C = coordType match {
          case "angle" => this.angle2Rad(p1.getX, p1.getY)
          case "rad" => (p1.getX, p1.getY)
        }
        val p2C = {
          coordType match {
            case "angle" => this.angle2Rad(p2.getX, p2.getY)
            case "rad" => (p2.getX, p2.getY)
          }
        }
        val Ed1 = earthRadius * cos(p1C._2)
        val dx = (p2C._1 - p1C._1) * Ed1
        val dy = (p2C._2 - p2C._2) * earthRadius
        sqrt(dx * dx + dy * dy)
      }
      case "cartesian" => {
        p1.distance(p2)
      }
    }
  }

//  def distance2D(p1: (Double, Double), p2: (Double, Double), distanceType: String = "sphere", coordType: String = "angle"): Double = {
//    distanceType match {
//      case "sphere" => {
//        val earthRadius = 6371393.0
//        val p1C = coordType match {
//          case "angle" => this.angle2Rad(p1._1, p1._2)
//          case _ => (p1._1, p1._2)
//        }
//        val p2C = {
//          coordType match {
//            case "angle" => this.angle2Rad(p2._1, p2._2)
//            case _ => (p2._1, p2._2)
//          }
//        }
//        val Ed1 = earthRadius * cos(p1C._2)
//        val dx = (p2C._1 - p1C._1) * Ed1
//        val dy = (p2C._2 - p2C._2) * earthRadius
//        sqrt(dx * dx + dy * dy)
//      }
//      case _ => {
//        sqrt(pow(p1._1 - p2._1, 2) + pow(p1._2 - p2._2, 2))
//      }
//    }
//  }

  /**
   *
   * @param point 所在位置（经纬度）
   * @param distance 球面距离
   * @return 经纬度距离（度）
   */
  def degreeDistance(point: Point, distance: Double): Double = {
    val R = 6371393
    val unitLengthLat = Pi * R * cos(point.getY.toRadians) / 180
    val unitLengthLng = Pi * R / 180
    distance / unitLengthLng
  }

  /**
   * 点到直线的距离
   *
   * @param p
   * @param line
   * @param distanceType
   * @return
   */
  def distancePointToLine2D(p: Point, line: LineString, distanceType: String = "sphere", coordType: String = "angle"): Double = {
    if (!Array("sphere", "cartesian").contains(distanceType)) {
      throw new Exception
    }
    if (line.getNumPoints != 2) {
      throw new IndexOutOfBoundsException
    } else {
      val pedalPoint = this.pedal(p, line)
      distance2D(p, pedalPoint, distanceType, coordType)
    }
  }

  /**
   * 求任意一点到某线段的垂足
   *
   * @param p
   * @param line
   * @return pedalPoint 垂足点对象
   */
  def pedal(p: Point, line: LineString): Point = {
    if (line.getNumPoints != 2) {
      throw new IndexOutOfBoundsException
    } else {
      val p1 = line.getStartPoint
      val p2 = line.getEndPoint
      if (p1.getX == p2.getX) {
        this.createPoint(p1.getX, p.getY)
      } else if (p1.getY == p2.getY) {
        this.createPoint(p.getX, p1.getY)
      } else {
        val k = (p2.getY - p1.getY) / (p2.getX - p1.getX)
        val b = p1.getY - k * p1.getX
        val k2 = -1.0 / k
        val b2 = p.getY - k2 * p.getX
        val cx = (b2 - b) / (k - k2)
        val cy = k * cx + b
        this.createPoint(cx, cy)
      }
    }
  }

  /**
   * 两点之间等间距分布n个点的几何
   *
   * @param p1
   * @param p2
   * @param nInterval
   * @return pointsSet
   */
  def equalIntervalPoints(p1: Point, p2: Point, nInterval: Int): Array[Point] = {
    val deltaX = (p2.getX - p1.getX) / (nInterval + 1)
    val deltaY = (p2.getY - p1.getY) / (nInterval + 1)
    val xs = (1 to nInterval).map(i => i * deltaX + p1.getX)
    val ys = (1 to nInterval).map(i => i * deltaY + p1.getY)
    (xs zip ys).map(p => this.createPoint(p._1, p._2)).toArray
  }

  /**
   * 求椭圆上等弧度间隔的点集合
   *
   * @param origin
   * @param a 短半轴
   * @param b 长半轴
   * @param n 点数
   * @param distanceType 距离类型
   * @return
   */
  def ellipsePoints(origin: Point, a: Double, b: Double, n: Int = 32, distanceType: String = "cartesian"): Array[Point] = {
    val radInterval = 2 * Pi / n
    val rads = (0 until n).map(i => -Pi + i * radInterval)
    rads.map(theta => {
      val dx = a * cos(theta)
      val dy = b * sin(theta)
      pointByRadAndDistance(origin, theta, sqrt(dx * dx + dy * dy), distanceType = distanceType) // rad
    }).toArray
  }

  /**
   * 任意圆上的等弧度点集合
   * @param origin 圆心位置
   * @param r 半径
   * @param n 点数
   * @param distanceType 距离类型
   * @return 点数组
   */
  def circlePoints(origin: Point, r: Double, n: Int = 32, distanceType: String = "sphere"): Array[Point] = {
    val radInterval = 2 * Pi / n
    val rads = (0 until n).map(i => -Pi + i * radInterval)
    distanceType match {
      case "cartesian" => {
        rads.map(theta => {
          val dx = r * cos(theta)
          val dy = r * sin(theta)
          pointByRadAndDistance(origin, theta, sqrt(dx * dx + dy * dy), distanceType = distanceType) // rad
        }).toArray
      }
      case "sphere" => {
        val newP = this.pointByRadAndDistance(origin, Pi / 2, r)
        println(newP)
        val r2 = this.distance2D(newP, origin, distanceType = "cartesian")
        rads.map(theta => {
          val dx = r2 * cos(theta)
          val dy = r2 * sin(theta)
          this.pointByRadAndDistance(origin, theta, sqrt(dx * dx + dy * dy), distanceType = "cartesian") // rad
        }).toArray
      }
    }
  }

  /**
   * rad为方位角，距离为distance，在点p相对位置的另一点
   *
   * @param p
   * @param offset   正北方位角弧度
   * @param distance 距离（米或平面坐标单位）
   * @param distanceType 距离类型
   * @return p2 目标点
   */
  def pointByRadAndDistance(p: Point, offset: Double, distance: Double, coordType: String = "angle", distanceType: String = "sphere"): Point = {
    val newP = coordType match {
      case "angle" => angle2Rad(p)
      case "rad" => p
    }
    //    val rad = val newP = coordType match {
    //      case "angle" => angle2Rad(p)
    //      case "rad" => p
    //    }

    if (!Array("sphere", "cartesian").contains(distanceType)) {
      throw new Exception
    } else {
      distanceType match {
        case "sphere" => {
          val earthRadius = 6371393.0
          val r = abs(earthRadius * cos(newP.getY))
          val deltaX = sin(offset) * distance
          val deltaY = cos(offset) * distance
          val radX = deltaX / r
          val radY = deltaY / earthRadius
          val angleX = rad2Angle(radX, radY)._1
          val angleY = rad2Angle(radX, radY)._2
          this.createPoint(p.getX + rad2Angle(radX, radY)._1, p.getY + rad2Angle(radX, radY)._2)
        }
        case "cartesian" => {
          val deltaX = sin(offset) * distance
          val deltaY = cos(offset) * distance
          this.createPoint(p.getX + deltaX, p.getY + deltaY)
        }
      }
    }
  }

  /**
   * 计算某直线斜率对应的弧度值
   *
   * @param line
   * @return
   */
  def slopeRad(line: LineString): Double = {
    if (line.getNumPoints != 2) {
      throw new IndexOutOfBoundsException
    } else {
      val p1 = line.getStartPoint
      val p2 = line.getEndPoint
      val deltaX = p2.getX - p1.getX
      val deltaY = p2.getY - p1.getY
      if (deltaX == 0) Pi / 2
      else if (deltaY == 0) 0
      else {
        val f = atan(deltaY / deltaX)
        if (f > 0) f
        else Pi + f
      }
    }
  }

  /**
   * 线坐标逆时针排序
   *
   * @param line
   * @return
   */
  def counterClockWise(line: LineString, coordType: String = "angle"): LineString = {
    val newLine = coordType match {
      case "angle" => {
        this.createLineString(line.getCoordinates.map(c => {
          val xy = angle2Rad(c.x, c.y)
          this.createPoint(xy._1, xy._2)
        }))
      }
      case "rad" => {
        this.createLineString(line.getCoordinates.map(c => {
          this.createPoint(c.x, c.y)
        }))
      }
    }

    val downLeft = newLine.getCoordinates.minBy(_.y)
    //    println(downLeft)
    //    println(line.getCoordinates.minBy(_.y))
    val ccwLine = this.createLineString(
      newLine.getCoordinates.map(p => {
        val dx = p.x - downLeft.x
        val dy = p.y - downLeft.y
        val dist = math.sqrt(dx * dx + dy * dy)
        val A = {
          if (dist == 0) {
            0
          } else if (dx >= 0 & dy >= 0) {
            math.asin(math.abs(dy / dist))
          } else if (dx < 0 & dy >= 0) {
            math.Pi / 2 + math.asin(math.abs(dy / dist))
          } else if (dx < 0 & dy < 0) {
            math.Pi - math.asin(math.abs(dy / dist))
          } else {
            math.Pi * 2 - math.asin(math.abs(dy / dist))
          }
        }
        //        println(s"$p $A")
        (p, A)
      }).sortBy(_._2).map(pA => this.createPoint(pA._1.x, pA._1.y)))
    this.createLineString(ccwLine.getCoordinates.map(p => {
      val newP = rad2Angle(p.x, p.y)
      this.createPoint(newP._1, newP._2)
    }))
  }

  def tdimSort(line: LineString, coordType: String = "angle"): LineString = {
    //求多边形的重心
    //    val orthocenter = Point(plist.map(_.x).sum / plist.size, plist.map(_.y).sum / plist.size)
    val orthoCenter = this.createPoint(
      line.getCoordinates.map(_.x).sum / line.getNumPoints,
      line.getCoordinates.map(_.y).sum / line.getNumPoints)
    val x = orthoCenter.getX
    val y = orthoCenter.getY
    // 计算从v1到v2的夹角公式
    // θ=atan2(v1.y,v1.x)−atan2(v2.y,v2.x)
    val voatan2 = atan2(y, x)
    this.createLineString(
      line.getCoordinates.map(p => {
        // 计算向量夹角
        val theta: Double = voatan2 - atan2(p.y - y, p.x - x)
        (p, theta)
      })
        .sortBy(_._2).map(_._1).map(p => this.createPoint(p.x, p.y))) // 根据角度排序（顺逆时针都可以）
  }

  /**
   * 判断点与多边形的关系
   * true: 点在多边形内
   * false: 点在多边形外
   */
  val pointInPolygon: (Point, Polygon) => Boolean = (p: Point, polygon: Polygon) => polygon.contains(p)

  /**
   * 求直线与多边形的交点
   *
   * @param line
   * @param polygon
   * @return
   */
  def lineIntersectPolygonPoints(line: LineString, polygon: Polygon): Array[Point] = {
    line.intersection(polygon).getCoordinates.map(p => this.createPoint(p.x, p.y))
  }

  /**
   * 某点关于某直线的镜像(轴对称)点
   *
   * @param point
   * @param line
   * @return
   */
  def mirrorPoint(point: Point, line: LineString): Point = {
    val pedalPoint = pedal(point, line)
    val deltaX = point.getX - pedalPoint.getX
    val deltaY = point.getY - pedalPoint.getY
    val x = point.getX - 2 * deltaX
    val y = point.getY - 2 * deltaY
    this.createPoint(x, y)
  }

  /**
   * 在多边形的每条边上取n个点
   *
   * @param polygon
   * @param n
   * @return
   */
  def getPointsOnPolygon(polygon: Polygon, n: Int): Array[Point] = {
    val vertices = polygon.getCoordinates.map(p => this.createPoint(p.x, p.y))
    val verticesBuffer = new ArrayBuffer[Point]()
    vertices.foreach(x => verticesBuffer.append(x))
    //    verticesBuffer.append(vertices.head)
    val pointsOnPolygon = new ArrayBuffer[Point]()
    verticesBuffer.sliding(2).map(ps => {
      val p0 = ps(0)
      val pp = new ArrayBuffer[Point]
      pp.append(p0)
      equalIntervalPoints(ps(0), ps(1), n).foreach(p => pp.append(p))
      pp.toArray
    }).reduceLeft(Array.concat(_, _)).foreach(p => pointsOnPolygon.append(p))
    pointsOnPolygon.append(vertices.last)
    pointsOnPolygon.toArray
  }

  def pointRelatesVector(point: Point, line: LineString): Int = {
    val p1 = line.getStartPoint
    val p2 = line.getEndPoint
    val crossProduct = (p2.getX - p1.getX) * (point.getY - p1.getY) - (point.getX - p1.getX) * (p2.getY - p1.getY)
    if (crossProduct == 0) 0
    else if (crossProduct > 0) -1
    else 1
  }

  /**
   * 直线分割多边形得到交线和分割后的两个多边形
   *
   * @param line
   * @param polygon
   * @return
   */
  def splitPolygon(line: LineString, polygon: Polygon): (LineString, Polygon, Polygon) = {

    // 求得直线与目标多边形的交点连线段
    val interLine = this.createLineString(this.lineIntersectPolygonPoints(line, polygon))
    val leftPoints = new ArrayBuffer[Point]()

    // 在连线左边的顶点
    polygon.getCoordinates.slice(0, polygon.getNumPoints - 1).map(p => this.createPoint(p.x, p.y))
      .filter(p => this.pointRelatesVector(p, interLine) == -1)
      .foreach(p => leftPoints.append(p))
    leftPoints.append(interLine.getStartPoint)
    leftPoints.append(interLine.getEndPoint)
    val leftPolygon = this.createPolygon(
      this.counterClockWise(this.createLineString(leftPoints.toArray)))

    val rightPoints = new ArrayBuffer[Point]()
    // 在连线上或右边的顶点
    polygon.getCoordinates.map(p => this.createPoint(p.x, p.y))
      .filter(p => this.pointRelatesVector(p, interLine) == 1)
      .foreach(p => rightPoints.append(p))
    rightPoints.append(interLine.getStartPoint)
    rightPoints.append(interLine.getEndPoint)
    val rightPolygon = this.createPolygon(this.counterClockWise(this.createLineString(rightPoints.toArray)))
    (interLine, leftPolygon, rightPolygon)
  }

  def getConvexHullPoints(points: Array[Point]): Array[Point] = {
    convexHull(points.map(p => (p.getX, p.getY))).map(p => this.createPoint(p._1, p._2))
  }

  def convexHull(points: Array[(Double, Double)]): Array[(Double, Double)] = {
    // 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.
    // Returns a positive value, if OAB makes a counter-clockwise turn,
    // negative for clockwise turn, and zero if the points are collinear.
    def cross(o: (Double, Double), a: (Double, Double), b: (Double, Double)): Double = {
      (a._1 - o._1) * (b._2 - o._2) - (a._2 - o._2) * (b._1 - o._1)
    }

    val distinctPoints = points.distinct

    // No sorting needed if there are less than 2 unique points.
    if (distinctPoints.length < 2) {
      return points
    } else {

      val sortedPoints = distinctPoints.sorted

      // Build the lower hull
      val lower = ArrayBuffer[(Double, Double)]()
      for (i <- sortedPoints) {
        while (lower.length >= 2 && cross(lower(lower.length - 2), lower(lower.length - 1), i) <= 0) {
          lower -= lower.last
        }
        lower += i
      }

      // Build the upper hull
      val upper = ArrayBuffer[(Double, Double)]()
      for (i <- sortedPoints.reverse) {
        while (upper.size >= 2 && cross(upper(upper.length - 2), upper(upper.length - 1), i) <= 0) {
          upper -= upper.last
        }
        upper += i
      }

      // Last point of each list is omitted because it is repeated at the beginning of the other list.
      lower -= lower.last
      upper -= upper.last

      // Concatenation of the lower and upper hulls gives the convex hull
      (lower ++= upper).toArray
    }
  }

  def isPointInGeometry(point: Point, geometry: Geometry, withBuffer: Double = 0): Boolean = {
    geometry.buffer(withBuffer).contains(point)
  }

  def centroid(points: Array[(Double, Double)]): (Double, Double) = {
    //    points.map(p=> (p._1 / points.length, p._2 / points.length)).reduce((p, q)=> (p._1 + q._1, p._2 + q._2))
    val x = points.map(_._1).sum / points.length
    val y = points.map(_._2).sum / points.length
    (x, y)
  }
  def centroid(points: Array[Point]): Point = {
    val x = points.map(_.getX).sum / points.length
    val y = points.map(_.getY).sum / points.length
    this.createPoint(x, y)
  }

  def vectorAngleByOrigin(V: (Point, Point)): Double = {
    val R = this.distance2D(V._1, V._2, distanceType = "cartesian")
    val x = V._2.getX - V._1.getX
    val y = V._2.getY - V._1.getY
    val t = abs(x) / R
    if (x >= 0 && y >= 0) acos(t)
    else if(x>=0 && y < 0) 2 * Pi - acos(t)
    else if (x < 0 && y >= 0) Pi - acos(t)
    else Pi + acos(t)
  }

  // 地球上任意椭圆
  def arbitraryEllipse(p1: Point, p2:Point, a:Double, b:Double, n:Int = 32): Polygon = {
    val center = this.createPoint(p1.getX / 2 + p2.getX / 2, p1.getY / 2 + p2.getY / 2)
    val rotateAngle = vectorAngleByOrigin((p1, p2))
    val pOnE = this.ellipsePoints(this.createPoint(0, 0), a, b, 34).map(point => {
      this.createPoint(
        point.getX * cos(rotateAngle) - point.getY * sin(rotateAngle),
        point.getX * sin(rotateAngle) + point.getY * cos(rotateAngle)
      )
    }).map(point => this.createPoint(
      point.getX + center.getX,
      point.getY + center.getY
    ))
    this.createPolygon(this.createLineString(pOnE))
  }

}
