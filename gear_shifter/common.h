
#ifndef COMMON_H
#define COMMON_H


const char STARTUP_MSG = 'S';
const char SHUTDOWN_MSG = 'X';
const char ACKNOWLEDGE_MSG = 'A';
const char ERROR_MSG = 'E';
const char DEBUG_MSG = 'D';
const char GEAR_CHANGING_MSG = 'C';
const char GEAR_CHANGED_MSG = 'G';

void reportError(String message);
void sendMessage(String type, String message);


#endif   // COMMON_H