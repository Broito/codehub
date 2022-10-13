package org.example
import org.apache.spark.sql.SparkSession

object create_dataframe extends App{
  val spark:SparkSession = SparkSession.builder()
    .master("local[1]").appName("SparkByExamples.com")
    .getOrCreate()

  import spark.implicits._
  val columns = Seq("language","users_count")
  val data = Seq(("Java", "20000"), ("Python", "100000"), ("Scala", "3000"))

  val dfFromData1 = data.toDF()
  println(dfFromData1)
}
