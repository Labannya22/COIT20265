# NF-CSE-CIC-IDS2018-v2 Processing

## Why We Used NF-CSE-CIC-IDS2018-v2

NF-CSE-CIC-IDS2018-v2 provides a second and different source of labelled network traffic. This helps the group investigate whether the intrusion-detection approach can generalise beyond UNSW-NB15. It is also suitable because it represents both normal and attack traffic using detailed NetFlow attributes. Using a second dataset produces stronger evidence than evaluating the project on only one traffic environment.

## Dataset Understanding

The original CSV is approximately 3 GB and contains 18,893,708 network-flow records. Each row represents a network flow. Its columns describe properties such as source and destination ports, protocol, packet counts, transferred bytes, flow duration, TCP flags and other traffic statistics. The dataset also contains a binary label identifying normal or attack traffic and an attack-name field.

The key technical challenge was its size. Loading the complete file into Colab memory could cause the runtime to disconnect. Therefore, I processed it in chunks of 200,000 rows, allowing every row to be inspected while controlling memory usage.
