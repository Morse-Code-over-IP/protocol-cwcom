/**
 * @file cwprotocol.h
 * @brief Definition of a communication protocol for client-server interaction.
 */

/**
 * @def INTERFACE_VERSION
 * @brief String indicating the version of the interface protocol.
 */

/**
 * @def DIS
 * @brief Disconnect command code.
 */

/**
 * @def DAT
 * @brief Data transmission command code.
 */

/**
 * @def CON
 * @brief Connect command code.
 */

/**
 * @def ACK
 * @brief Acknowledgment command code.
 */

/**
 * @def SIZE_COMMAND_PACKET
 * @brief Size of the command packet structure.
 */

/**
 * @def SIZE_DATA_PACKET
 * @brief Total size of the data packet structure.
 */

/**
 * @def SIZE_DATA_PACKET_PAYLOAD
 * @brief Size of the payload within the data packet structure.
 */

/**
 * @def SIZE_ID
 * @brief Size of the ID field in the packet structures.
 */

/**
 * @def SIZE_STATUS
 * @brief Size of the status field in the packet structures.
 */

/**
 * @def SIZE_CODE
 * @brief Size of the code array in the data packet structure.
 */

/**
 * @struct command_packet_format
 * @brief Structure for command packets used for (dis-)connecting to KOB servers.
 */

/**
 * @struct data_packet_format
 * @brief Structure for data packets containing various fields for communication.
 */

/**
 * @fn int prepare_id(struct data_packet_format *id_packet, char *id)
 * @brief Prepares an ID packet with the given ID and default values for other fields.
 * @param id_packet Pointer to the data packet structure to be prepared.
 * @param id Pointer to the ID string.
 * @return 0 on success.
 */

/**
 * @fn int prepare_tx(struct data_packet_format *tx_packet, char *id)
 * @brief Prepares a data packet for transmission with the given ID and default values for other fields.
 * @param tx_packet Pointer to the data packet structure to be prepared.
 * @param id Pointer to the ID string.
 * @return 0 on success.
 */

/**
 * @fn void identifyclient(void)
 * @brief Connects to the server and sends the client's ID packet.
 */

/**
 * @fn int send_latch(void)
 * @brief Sends a latch command to the server using a data packet.
 * @return 0 on success.
 */

/**
 * @fn int send_unlatch(void)
 * @brief Sends an unlatch command to the server using a data packet.
 * @return 0 on success.
 */

/**
 * @var struct command_packet_format connect_packet
 * @brief Structure for the connection command packet.
 */

/**
 * @var struct command_packet_format disconnect_packet
 * @brief Structure for the disconnection command packet.
 */

/**
 * @var struct data_packet_format id_packet
 * @brief Data packet structure for the client's ID.
 */

/**
 * @var struct data_packet_format rx_data_packet
 * @brief Data packet structure for received data.
 */

/**
 * @var struct data_packet_format tx_data_packet
 * @brief Data packet structure for transmitted data.
 */

/**
 * @var int tx_sequence
 * @brief Sequence number for transmitted packets.
 */

/**
 * @var int rx_sequence
 * @brief Sequence number for received packets.
 */

/**
 * @var int fd_socket
 * @brief File descriptor for the socket connection.
 */

#include <stdio.h>
#include <sys/socket.h>

#include "cwprotocol.h"

