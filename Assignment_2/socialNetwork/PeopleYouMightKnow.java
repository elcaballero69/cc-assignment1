import java.io.IOException;
import java.util.StringTokenizer;
import java.util.*;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;


// People You Might Know Algorithm
// Class templates based on Hadoop's WordCount.java example
// NOTE: No IDs allowed larger than 65535, if needed edit to longs
public class PeopleYouMightKnow {
  public static class PYMKMapper
       extends Mapper<Intwritable, Text, Intwritable, Intwritable>{
    public void map(Object key, Text value,
     Context context) throws IOException, InterruptedException {
      String[] input = value.toString.split("\t");
      // Parse user here already, since sometimes users cannot have friends
      Integer user = Integer.parseInt(input[0]);
      // If a user has friends, map the user to each of these friends
      if (input.length == 2){
        // Friends are comma separated
        String[] friends = input[1].split(",");
        // Write entry that this user is already friends with all his friend
        for (int x=0; x<friends.length; x++){
          Integer friend = Integer.parseInt(friends[x]);
          Integer friend_and_status = -1 | ( friend << 16 );
          context.write(new IntWritable(user), new IntWritable(friend_and_status));
        }
        // Write entry for all his friends that they are mutual friends through user
        for (int x = 0; x < (friends.length - 1); x++){
          for (int y = x + 1; y < friends.length; y++){
            Integer friend0 = Integer.parseInt(friends[x]);
            Integer friend1 = Integer.parseInt(friends[y]);
            Integer friend0_and_status = user | ( friend0 << 16 );
            Integer friend1_and_status = user | ( friend1 << 16 );
            // Write potential friendship in both directions
            context.write(new IntWritable(friend0), new IntWritable(friend1_and_status));
            context.write(new IntWritable(friend1), new IntWritable(friend0_and_status));
          }
        }
      }
      else if (input.length == 1){
        context.write(new IntWritable(user), new IntWritable(-2));
      }
    }
  }

  public static class PYMKReducer
       extends Reducer<IntWritable, IntWritable, InWritable, Text> {
    public void reduce(IntWritable key, Iterable<IntWritable> values,
                       Context context
                       ) throws IOException, InterruptedException {
      // First check if you found someone without friends
      // We cannot give them suggestions
      if ((values.size() == 1) && (values[0] == -2)){
        Arraylist<Integer> sorted_suggetions = new ArrayList<Integer>();
        context.write(key.toString(), empty_suggetions.toString());
      } else{
        // Hashmap of all intermediate values indicating a mutual friend between 
        // person0 (key) and anyone else
        // If person0 is already friends with someone else an entry will be added that is null
        Map<Integer, ArrayList<Integer>> hashMap = new HashMap<Integer, ArrayList<Integer>>();
        for(int i = 0; i < values.length; i++){
          Integer person0 = key;
          Integer person1 = values[i] & 0xFFFF;
          Integer person2 = (values[i] >> 16) & 0xFFFF;
          boolean a = (person1 != -1);
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
        // Remove keys with value null, they are already friends
        // Also change list of mutual friends to amount of mutual friends
        Map<Integer, ArrayList<Integer>> suggestions = new HashMap<Integer, ArrayList<Integer>>();
        for (Map.Entry<Integer, Integer> entry : hashMap.entrySet()) {
          Integer key0 = entry.getKey();
          Integer value = entry.getValue();
          if (value != null){
            suggestions.put(key0, value.size());
          }
        }
        // Get the 10 best suggestions, if less than 10 suggestions available 
        Arraylist<Integer> sorted_suggetions = new ArrayList<Integer>();
        while((sorted_suggestions.size() < 10) && (suggestions.size() > 0)){
          // Get person with most mutual friends
          Key key0 = Collections.max(suggestions.entrySet(), Map.Entry.comparingByValue()).getKey();
          // Add this person to the sorted suggestions
          sorted_suggestions.add((int)key0);
          // Remove this person from suggestions
          suggestions.remove(key0);
        }
        // Make 10 suggestions to a string
        String string_suggestions = String.join(",", sorted_suggestions);
        // Pass the key and its suggested friends
        context.write(key.toString(), string_suggestions);
      }
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