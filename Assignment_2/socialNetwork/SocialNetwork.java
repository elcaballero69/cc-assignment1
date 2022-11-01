import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class PeopleYouMightKnow {

  public static class PYMKMapper
       extends Mapper<Object, Text, Text, IntWritable>{

    public void map(Object key, Text value,
     Context context) throws IOException, InterruptedException {
        // Split inputs on the tabs (these separate the user and its friends)
        String[] split_value = value.toString().split("\t");
        Int user = split_value[0]
        List<Int> friends = split_value[1]


    }
  }

  public static class PYMKReducer
       extends Reducer<Text,IntWritable,Text,IntWritable> {
    private IntWritable result = new IntWritable();

    public void reduce(Text key, Iterable<IntWritable> values,
                       Context context
                       ) throws IOException, InterruptedException {
   
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "peopleyoumightknow");
    job.setJarByClass(PeopleYouMightKnow.class);
    job.setMapperClass(PYMKMapper.class);
    job.setCombinerClass(PYMKReducer.class);
    job.setReducerClass(PYMKReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }

    




}