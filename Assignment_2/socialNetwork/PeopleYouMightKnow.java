import java.io.IOException;
import java.util.StringTokenizer;
import java.util.*;
import java.io.*;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;


// People You Might Know Algorithm
// Class templates based on Hadoop's WordCount.java example
// NOTE: No IDs allowed larger than 65533, if needed edit to longs
public class PeopleYouMightKnow {
  public static class PYMKMapper
       extends Mapper<LongWritable, Text, IntWritable, IntWritable>{
    @Override
    public void map(LongWritable key, Text value,
     Context context) throws IOException, InterruptedException {
      System.out.println("map started");
      String[] input = value.toString().split("\t");
      // Parse user here already, since sometimes users cannot have friends
      Integer user = Integer.parseInt(input[0]);
      // If a user has friends, map the user to each of these friends
      if (input.length == 2){
        System.out.println("input length is 2");
        // Friends are comma separated
        String[] friends = input[1].split(",");
        // Write entry that this user is already friends with all his friend
        for (int x=0; x<friends.length; x++){
          Integer friend = Integer.parseInt(friends[x]);
          Integer friend_and_status = 65534 | ( friend << 16 );
          context.write(new IntWritable(user), new IntWritable(friend_and_status));
        }
        // Write entry for all his friends that they are mutual friends through user
        for (int x = 0; x < (friends.length - 1); x++){
          for (int y = x + 1; y < friends.length; y++){
            Integer friend0 = Integer.parseInt(friends[x]);
            Integer friend1 = Integer.parseInt(friends[y]);
            int friend0_and_status = user | ( friend0 << 16 );
            int friend1_and_status = user | ( friend1 << 16 );
            // Write potential friendship in both directions
            context.write(new IntWritable(friend0), new IntWritable(friend1_and_status));
            context.write(new IntWritable(friend1), new IntWritable(friend0_and_status));
          }
        }
      }
      else if (input.length == 1){
        context.write(new IntWritable(user), new IntWritable(-1));
      }
    }
  }

  public static class PYMKReducer
       extends Reducer<IntWritable, IntWritable, IntWritable, Text> {
    @Override
    public void reduce(IntWritable key, Iterable<IntWritable> values,
                       Context context
                       ) throws IOException, InterruptedException {
      // Hashmap of all intermediate values indicating a mutual friend between 
      // person0 (key) and anyone else
      // If person0 is already friends with someone else an entry will be added that is null
      Map<Integer, ArrayList<Integer>> hashMap = new HashMap<Integer, ArrayList<Integer>>();
      for(IntWritable value : values){
        Integer val = value.get();
        if (val == -1){
          ArrayList<Integer> empty_suggetions = new ArrayList<Integer>();
          context.write(key, new Text(empty_suggetions.toString()));
        }else{
          int person0 = key.get();
          Integer person1 = val & 0xFFFF;
          Integer person2 = (val >> 16) & 0xFFFF;
          boolean a = (person1 != 65534);
          boolean b = (hashMap.containsKey(person2));
          // If person1 is -1 it means person0 and person2 are already friends
          if ( a && !b ){
            // CASE 1
            // This entry does not show that the persons would be friends
            // There is no entry yet in the hashmap
            ArrayList<Integer> al= new ArrayList<Integer>();
            hashMap.put(person2, al);
            hashMap.get(person2).add(person1);
          } else if ( a && b ){
            // CASE 2
            // This entry does not show that the persons would be friends
            // There is an entry in the hashmap that is not null
            // Before we add, we need to check if no previous entry indicated
            if (hashMap.get(person2) != null){
              hashMap.get(person2).add(person1);
            }
          } else if ( !a ){
            // CASE 3
            // Person0 and person1 are already friends
            hashMap.put(person2, null);
          }
        }
      }
      // Remove keys with value null, they are already friends
      // Also change list of mutual friends to amount of mutual friends
      Map<Integer, Integer> suggestions = new HashMap<Integer, Integer>();
      for (Map.Entry<Integer, ArrayList<Integer>> entry : hashMap.entrySet()) {
        Integer key0 = entry.getKey();
        ArrayList<Integer> val0 = entry.getValue();
        if (val0 != null){
          suggestions.put(key0, val0.size());
        }
      }
      // Get the 10 best suggestions, if less than 10 suggestions available 
      ArrayList<String> sorted_suggestions = new ArrayList<String>();
      while((sorted_suggestions.size() < 10) && (suggestions.size() > 0)){
        // Get maximum number of mutual friends
        Integer best_key = 65534;
        Integer val_best = Collections.max(suggestions.entrySet(), Map.Entry.comparingByValue()).getValue();
        for (Map.Entry<Integer, Integer> entry : suggestions.entrySet()) {
          Integer key0 = entry.getKey();
          Integer val0 = entry.getValue();
          if ((val0 == val_best) && key0 < best_key){
            best_key = key0;
          }
        }
        // Add this person to the sorted suggestions
        sorted_suggestions.add(best_key.toString());
        // Remove this person from suggestions
        suggestions.remove(best_key);
      }
      // Make 10 suggestions to a comma separated string
      String comma_separated_suggestions = String.join(",", sorted_suggestions);
      // Pass the key and its suggested friends
      context.write(key, new Text(comma_separated_suggestions));
      
    }
  }

  public static void main(String[] args) throws Exception {
    // Create new Job configuration
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "PeopleYouMightKnow");
    // Set Mapper, Combiner and Reducer classes
    job.setJarByClass(PeopleYouMightKnow.class);
    job.setMapperClass(PYMKMapper.class);
    // job.setCombinerClass(PYMKReducer.class);
    job.setReducerClass(PYMKReducer.class);
    // Input and Output formats
    job.setInputFormatClass(TextInputFormat.class);
    job.setOutputFormatClass(TextOutputFormat.class);
    // Set output types of the reducer
    job.setOutputKeyClass(IntWritable.class);
    job.setOutputValueClass(IntWritable.class);
    // Set output types of the mapper
    // job.setMapOutputKeyClass(IntWritable.class);
    // job.setMapOutputValueClass(IntWritable.class);

    FileSystem newOutFileSystem = new Path(args[1]).getFileSystem(conf);
    newOutFileSystem.delete(new Path(args[1]), true);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}