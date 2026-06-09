#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Define a maximum length for song details
#define MAX_LENGTH 256

typedef struct Song {
    char name[MAX_LENGTH];
    char artist[MAX_LENGTH];
    char url[MAX_LENGTH];
    struct Song* next;
    struct Song* prev; // Add pointer to the previous node
} Song;

Song* head = NULL;
Song* tail = NULL; // Add pointer to the tail of the list

void addSong(const char* name, const char* artist, const char* url) {
    Song* newSong = (Song*)malloc(sizeof(Song));
    if (newSong == NULL) {
        fprintf(stderr, "Failed to allocate memory for new song.\n");
        exit(1);
    }
    strncpy(newSong->name, name, MAX_LENGTH - 1);
    strncpy(newSong->artist, artist, MAX_LENGTH - 1);
    strncpy(newSong->url, url, MAX_LENGTH - 1);
    newSong->name[MAX_LENGTH - 1] = '\0';
    newSong->artist[MAX_LENGTH - 1] = '\0';
    newSong->url[MAX_LENGTH - 1] = '\0';
    newSong->next = NULL;
    newSong->prev = tail; // Set the previous pointer to the current tail

    if (head == NULL) {
        head = newSong;
        tail = newSong;
    } else {
        tail->next = newSong;
        tail = newSong;
    }
    printf("Added song: %s - %s\n", name, artist);
}

void loadPlaylist() {
    FILE* file = fopen("playlist.txt", "r");
    if (file != NULL) {
        char line[MAX_LENGTH * 3]; // Enough space for name, artist, and url
        while (fgets(line, sizeof(line), file)) {
            char name[MAX_LENGTH], artist[MAX_LENGTH], url[MAX_LENGTH];
            sscanf(line, "%255[^|]|%255[^|]|%255[^\n]", name, artist, url);
            addSong(name, artist, url);
        }
        fclose(file);
        printf("Playlist loaded from file.\n");
    }
}

void savePlaylist() {
    FILE* file = fopen("playlist.txt", "w");
    if (file != NULL) {
        Song* temp = head;
        while (temp != NULL) {
            fprintf(file, "%s|%s|%s\n", temp->name, temp->artist, temp->url);
            temp = temp->next;
        }
        fclose(file);
        printf("Playlist saved to file.\n");
    }
}

void printPlaylist() {
    Song* temp = head;
    while (temp != NULL) {
        printf("%s - %s\n", temp->name, temp->artist);
        temp = temp->next;
    }
}

void deleteSong(const char* name) {
    Song* temp = head;
    while (temp != NULL && strcmp(temp->name, name) != 0) {
        temp = temp->next;
    }
    if (temp != NULL) {
        if (temp->prev != NULL) {
            temp->prev->next = temp->next;
        } else {
            head = temp->next;
        }
        if (temp->next != NULL) {
            temp->next->prev = temp->prev;
        } else {
            tail = temp->prev;
        }
        free(temp);
        savePlaylist();
        printf("Song deleted: %s\n", name);
    }
}

void freePlaylist() {
    Song* temp;
    while (head != NULL) {
        temp = head;
        head = head->next;
        free(temp);
    }
}

int main(int argc, char* argv[]) {
    loadPlaylist();
    if (argc == 2 && strcmp(argv[1], "print") == 0) {
        printPlaylist();
    } else if (argc == 3 && strcmp(argv[1], "delete") == 0) {
        deleteSong(argv[2]);
    } else if (argc == 4) {
        addSong(argv[1], argv[2], argv[3]);
        savePlaylist();
    } else {
        fprintf(stderr, "Usage: %s <name> <artist> <url> | %s print | %s delete <name>\n", argv[0], argv[0], argv[0]);
    }
    freePlaylist();
    return 0;
}