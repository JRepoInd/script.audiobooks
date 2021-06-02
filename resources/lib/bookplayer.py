# -*- coding: utf-8 -*-
import xbmc

# Import the common settings
from settings import log
from database import AudioBooksDB


#######################################
# Custom Player to play the audio book
#######################################
class BookPlayer(xbmc.Player):

    # Calls the media player to play the selected item
    @staticmethod
    def playAudioBook(audioBookHandler, startTime=-1, chapter=0):
        log("BookPlayer: Playing audio book = %s" % audioBookHandler.getFile())

        bookPlayer = BookPlayer()

        playlist = audioBookHandler.getPlayList(startTime, chapter)

        bookPlayer.play(playlist)

        # Don't allow this to loop forever
        loopCount = 3000
        while (not bookPlayer.isPlaying()) and (loopCount > 0):
            xbmc.sleep(1)
            loopCount -= 1

        # Looks like the audiobook never started for some reason, do not go any further
        if loopCount == 0:
            return

        currentTime = 0
        currentFile = ''
        totalTrackTime = 0

        waitingForComplete = 0
        # Wait for the player to stop
        while waitingForComplete < 30:
            # There is a small gap when switching between different items in the same
            # playlist where it records it as not playing, so we need to give it a little
            # bit of time to start playing the next item in the playlist if there is one
            if bookPlayer.isPlaying():
                # Keep track of where the current track is up to
                try:
                    currentTime = int(bookPlayer.getTime())
                    currentFile = bookPlayer.getPlayingFile()
                    totalTrackTime = bookPlayer.getTotalTime()
                    waitingForComplete = 0
                except:
                    # If we get an exception there it is most probably because there is
                    # a small gap between checking if something is playing and getting
                    # each of the values
                    waitingForComplete += 1
            else:
                waitingForComplete += 1
            xbmc.sleep(10)

        # Record the time that the player actually stopped
        log("BookPlayer: Played to time = %d, file = %s, totalTime = %s" % (currentTime, currentFile, totalTrackTime))

        # Get the chapter number that was playing
        chapterPosition = audioBookHandler.getChapterPosition(currentFile)
        log("BookPlayer: Chapter position is %d" % chapterPosition)

        if (currentTime > 0) or (chapterPosition > 1):
            bookComplete = False
            duration = audioBookHandler.getTotalDuration()
            log("BookPlayer: Total book duration is %d" % duration)
            if duration > 1 and currentTime > (duration - 60):
                log("BookPlayer: Marking entire book as complete")
                bookComplete = True

            # If dealing with multiple files for a single book, need to check if the entire
            # book is complete
            if (
                chapterPosition == len(audioBookHandler.getChapterDetails())
                and (currentTime + 60) > totalTrackTime
            ):
                log("BookPlayer: Marking book as complete")
                bookComplete = True

            audiobookDB = AudioBooksDB()
            audiobookDB.setPosition(audioBookHandler.getFile(), currentTime, chapterPosition, bookComplete)
            del audiobookDB
