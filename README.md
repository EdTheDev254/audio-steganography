# Audio Steganography

The purpose of this project is to use LSB (Least Significant Bit) encoding to hide a significant amount of text data within a standard .wav audio file without creating any perceptible audio artifacts. The objective was to develop a program capable of embedding a text file containing several thousand characters into a carrier audio file in a way that is truly covert. The project is defined not by whether the data can be hidden and recovered, but by whether the resulting audio file is indistinguishable from the original to a human listener.

# Technical Discoveries

Through experimentation, I discovered a practical threshold where the interleaved method becomes truly effective. A step rate of 100 or more is required to ensure the modifications are sparse enough to be imperceptible. This is the tipping point where the "hiss" somehow dissolves.

# What the Program Does

- **Imports the Message:** Reads the secret message from an external, easily editable Python file (`message_container.py`), separating the data from the program logic.  
- **Provides a Full Analysis:** Before encoding, it inspects the `carrier.wav` file and reports its properties: Channels, Sample Rate, Bit Depth, and Duration.  
- **Calculates Dual Capacity:** It informs the user of two different limits:  
  - **Absolute Maximum:** The total amount of data the file can physically hold.  
  - **Stealth Capacity:** The recommended maximum data that can be hidden while maintaining a step rate of at least 100, ensuring no audible hiss.  
- **Warnings:** If the user tries to hide a message that exceeds the stealth capacity, the program warns that the result may be audible and asks for confirmation before proceeding.
