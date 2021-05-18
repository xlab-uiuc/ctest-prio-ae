library(agricolae)

args = commandArgs(trailingOnly=TRUE)

get_hsd <- function(fname, outfname) {
  
  t <- read.table(fname, sep='\t', header=TRUE)
  model.lm <- lm(score ~ tcp, data=t)
  model.av <- aov(model.lm)
  tukey.test <- HSD.test(model.av, trt='tcp')
  groups = tukey.test$groups
  write.table(groups, file=outfname, sep='\t', quote=FALSE)
}

get_hsd(args[1], args[2])
