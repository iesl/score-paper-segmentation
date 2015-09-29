package edu.umass.cs.iesl.score_paper_segmentation

import java.io.File


class Score(var headerScore: Double, var bodyScore: Double, var referencesScore: Double) {
  
  def +=(other: Score) = {
    headerScore += other.headerScore
    bodyScore += other.bodyScore
    referencesScore += other.referencesScore
  }
  
}

object Scorer {

  def scorePaper(predicted: Paper, gold: Paper) = {
    val headerScore = JaccardSimilarity(predicted.headerBigrams, gold.headerBigrams)
    val bodyScore = JaccardSimilarity(predicted.bodyBigrams,gold.bodyBigrams)
    val refScore = JaccardSimilarity(predicted.referencesBigrams,gold.referencesBigrams)
    new Score(headerScore,bodyScore,refScore)
  }
  
  def scorePapers(predicted: Iterable[Paper], gold: Iterable[Paper]) = {
    val scores = predicted.zip(gold).map(f => scorePaper(f._1,f._2))
    scores
  }

  /**
   * USAGE:
   * ./Scorer predictedDir goldDir predictedEncoding goldEncoding
   * @param args
   */
  def main(args: Array[String]): Unit = {
    val predFiles = new File(args(0)).listFiles.filterNot(_.getName.startsWith(".")).sortBy(_.getName.split("\\.").head)//.take(1)
    val goldFiles = new File(args(1)).listFiles.filterNot(_.getName.startsWith(".")).sortBy(_.getName.split("\\.").head)//.take(1)
    val codecPred = args(2)
    val codecGold = args(3)
    
    val predicted = predFiles.map(Paper.apply(_,codecPred))
    val gold = goldFiles.map(Paper.apply(_,codecGold))
    
    val scores = scorePapers(predicted,gold)
    
    val finalScore = new Score(0.0,0.0,0.0)
    scores.foreach(finalScore += _)
    
    val numPapers = scores.size
    println(s"Number of Papers: $numPapers")
    println(s"Total Header Jaccard Similarity: ${finalScore.headerScore}")
    println(s"Average Header Jaccard Similarity: ${finalScore.headerScore/numPapers}")
    println(s"Total Body Jaccard Similarity: ${finalScore.bodyScore}")
    println(s"Average Body Jaccard Similarity: ${finalScore.bodyScore/numPapers}")
    println(s"Total References Jaccard Similarity: ${finalScore.referencesScore}")
    println(s"Average References Jaccard Similarity: ${finalScore.referencesScore/numPapers}")
  }
}





object JaccardSimilarity {
  def apply[T](A: Set[T], B: Set[T]) = {
    val denom = (A union B).size
    if (denom == 0)
      1.0
    else
      (A intersect B).size.toDouble / denom.toDouble
  }
}

class Paper(val headerString: String,
            val bodyString: String,
            val referencesString: String) {
  
  val headerBigrams  = Bigrams(headerString).toSet
  val bodyBigrams = Bigrams(bodyString).toSet
  val referencesBigrams = Bigrams(referencesString).toSet
  
} 

object Paper {

  def get(rawString: String, startFlag: String, endFlag: String) = {
    val rgx = s"#$startFlag(((?!#$endFlag).)*)[(#$endFlag)|$$]".r
    rgx.findAllMatchIn(rawString).map(_.group(1)).toIterable.headOption
  }

  def get(rawString: String, startFlag: String) = {
    val rgx = s"#$startFlag(.*)$$".r
    rgx.findAllMatchIn(rawString).map(_.group(1)).toIterable.headOption
  }
  
  /**
   * Load a paper object from a string 
   * @param rawString
   */
  def apply(rawString: String): Paper = {
    //val rgx = """^#Header(((?!#Header).)*)#Body(((?!#Body).)*)#References(((?!#References).)*)$""".r
    //val mtch = rgx.findAllMatchIn(rawString).next()
    val headerString =  get(rawString, "Header", "Body")
    val bodyString =  get(rawString, "Body", "References")
    val refString =  get(rawString, "References")
    if (headerString.isEmpty)
      println("WARNING: Empty Header.")
    if (bodyString.isEmpty)
      println("WARNING: Empty Body.")
    if (refString.isEmpty)
      println("WARNING: Empty References.")
    new Paper(headerString.getOrElse(""),bodyString.getOrElse(""),refString.getOrElse(""))
  }
  
  def apply(file: File, codec: String): Paper = {
    println(s"Reading file: ${file.getAbsolutePath}")
    apply(scala.io.Source.fromFile(file,codec).getLines().mkString(" "))
  }
  
}

  
object Bigrams {

  /**
   * The function call Bigrams(string) will return an iterable of
   * pairs of strings--the bigrams. The regex determines how the text 
   * is tokenized  
   * @param string
   * @param regex
   * @return
   */
  def apply(string: String, regex: String = "[^a-zA-Z]") = {
    val split = string.split(regex)
    split.zip(split.drop(1))
  }
  
  def main(args: Array[String]): Unit = {
    val codec = if (args.length > 1) args(1) else "UTF-8"
    println(apply(scala.io.Source.fromFile(new File(args(0)),codec).getLines().mkString(" ")).mkString("| "))
  }
  
}
