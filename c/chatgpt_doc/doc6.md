Command Packets (command_packet_format):

The command packets are used for specific actions like connecting to the server (CON), disconnecting from the server (DIS), acknowledging packets (ACK), etc.
The command_packet_format structure has a command field representing the type of command being sent.
When the receiver receives a packet, it examines the command field to identify the type of command being sent. For example, if command is CON, it indicates a connection command. If command is DIS, it indicates a disconnection command.
Data Packets (data_packet_format):

The data packets are used for transmitting Morse code messages.
The data_packet_format structure also has a command field, but in this context, it represents a data packet (DAT).
When the receiver receives a packet with command set to DAT, it knows that the packet contains Morse code data. The receiver then processes the Morse code elements (dots, dashes, and spaces) from the code field of the data_packet_format structure.
