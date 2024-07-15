## This script is runnable on Windows, and works (with slight modification) on Ubuntu and MacOS
## This script is used to read the mcap file and print the messages of the topics

# pip install mcap mcap-ros2-support matplotlib numpy pandas scipy
# mcap-ros2-support works on Windows too!

from mcap_ros2.decoder import DecoderFactory
from mcap_ros2.writer import Writer as McapWriter
from mcap.reader import make_reader
import sys


## This is not needed, but it is an alternative way to define the schema
SCHEMA_NAME_TF = "tf2_msgs/TFMessage"
## be careful with the indentation in SCHEMA
SCHEMA_TEXT_TF = """\
geometry_msgs/TransformStamped[] transforms
================================================================================
MSG: geometry_msgs/TransformStamped
std_msgs/Header header
string child_frame_id # the frame id of the child frame
Transform transform
================================================================================
MSG: std_msgs/Header
builtin_interfaces/Time stamp
string frame_id
================================================================================
MSG: geometry_msgs/Transform
Vector3 translation
Quaternion rotation
================================================================================
MSG: geometry_msgs/Vector3
float64 x
float64 y
float64 z
================================================================================
MSG: geometry_msgs/Quaternion
float64 x
float64 y
float64 z
float64 w"""



def read_mcap_channels(source_file):
    """Reads all channels from an MCAP file."""
    channels = []
    schema = []
    channel = []
    message = []
    ros_msg = []
    with open(source_file, "rb") as f:
        reader = make_reader(f, decoder_factories=[DecoderFactory()])
        channels = reader.get_summary().channels.items()
        for s, c, m, r in reader.iter_decoded_messages():
            # if(c.topic == "/tf"):
            # print("%s -- %d || %s" % (c.topic, m.log_time, r.transforms[0].transform.translation.x))
            schema.append(s)
            channel.append(c)
            message.append(m)
            ros_msg.append(r)
    print("Read %d channels from %s" % (len(channels), source_file))
    return schema, channel, message, ros_msg

def write_mcap_channels(destination_file, schema, channel, message, ros_msg):
    """Writes channels to an MCAP file."""
    # Open or create the destination MCAP file for writing
    with open(destination_file, 'wb') as dest:
        writer = McapWriter(dest)
        for m in message:
            # first log time
            first_log_time_sec = m.log_time // 1000000000
            first_log_time_nsec = m.log_time % 1000000000
            print("First log time: %d.%d" % (first_log_time_sec, first_log_time_nsec))
            break    
        seq_new = 0
        for s, c, m, r in zip(schema, channel, message, ros_msg):
            seq_new += 1
            # print("Writing message to %s %s" % (c.topic, s.data))
            try:
                i = seq_new
                # schema = writer.register_msgdef(SCHEMA_NAME_TF, SCHEMA_TEXT_TF)
                schema = writer.register_msgdef(s.name, (s.data).decode("utf-8"))
                writer.write_message(
                    topic=c.topic,
                    schema=schema,
                    message=r,
                    log_time=m.log_time,
                    publish_time=m.log_time,
                    sequence=seq_new,
                )
            except:
                print("Unexpected error: %s (%s)" % (sys.exc_info()[0], c.topic))
        writer.finish()
        print("Wrote %d channels to %s" % (len(channel), destination_file))

def main():
    source_file = 'C:\\Users\\he\\Downloads\\roundabout_dynamic_2024-06-18_09-13_0.mcap'
    destination_file = 'C:\\Users\\he\\Downloads\\roundabout_dynamic_new.mcap'
    
    # Read channels from the source MCAP file
    schema, channel, message, ros_msg = read_mcap_channels(source_file)
    
    # Write channels to the destination MCAP file
    write_mcap_channels(destination_file, schema, channel, message, ros_msg)

if __name__ == "__main__":
    main()