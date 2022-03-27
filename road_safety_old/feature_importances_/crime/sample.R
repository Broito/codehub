fPath<-"C:\\Users\\giscui\\Desktop\\demo.csv"
partionSample <- function(df_data, labelColName) {
  
  for (i in 1:5) {
    index <- which(df_data[labelColName] == i)
    set.seed(123)
    sample_index <- sample(2, index, replace = TRUE, prob = c(0.2, 0.8))
    train_index <- df_data[index==1, 2:39]
    test_index <- df_data[index==2, 2:39]
  }
}