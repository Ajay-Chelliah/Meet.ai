import React, { useState } from 'react';
import { View, Button, Text, StyleSheet } from 'react-native';
import { Audio } from 'expo-av';
import axios from 'axios';

export default function App() {
  const [recording, setRecording] = useState(null);
  const [message, setMessage] = useState('');

  // Start Recording Function
  const startRecording = async () => {
    try {
      console.log('Requesting permissions..');
      const permission = await Audio.requestPermissionsAsync();

      if (permission.status === 'granted') {
        console.log('Starting recording..');
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: true,
          playsInSilentModeIOS: true,
        });

        const { recording } = await Audio.Recording.createAsync(
          Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY
        );
        setRecording(recording);
        console.log('Recording started');
      } else {
        setMessage('Permission to access microphone denied.');
      }
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  };

  // Stop Recording Function
  const stopRecording = async () => {
    console.log('Stopping recording..');
    setRecording(undefined);
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();
    console.log('Recording stopped and stored at', uri);
    setMessage('Recording stored at: ' + uri);
    return uri;
  };

  // Upload Audio Function
  const sendAudio = async (uri) => {
    const formData = new FormData();
    formData.append('file', {
      uri,
      name: 'audio.m4a',
      type: 'audio/m4a'  // Change to m4a as Expo saves it in this format
    });

    try {
      const response = await axios.post('http://192.168.173.161:8081/process-audio/', 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      console.log('Audio sent successfully:', response.data);
      setMessage('Audio sent successfully');
    } catch (error) {
      console.error('Error sending audio:', error);
      setMessage('Error sending audio');
    }
  };

  // Transcribe Audio Function
  const transcribeAudio = async () => {
    try {
      const response = await axios.get('http://192.168.173.161:8081/transcribe-audio/');
      console.log('Transcription:', response.data);
      setMessage('Transcription: ' + response.data.transcription);
    } catch (error) {
      console.error('Error transcribing audio:', error);
      setMessage('Error transcribing audio');
    }
  };

  // Extract Details Function
  const extractDetails = async () => {
    try {
      const response = await axios.get('http://192.168.173.161:8081/extract-details/');
      console.log('Extracted details:', response.data);
      setMessage('Extracted details: ' + JSON.stringify(response.data));
    } catch (error) {
      console.error('Error extracting details:', error);
      setMessage('Error extracting details');
    }
  };

  // Send Email Function
  const sendEmail = async () => {
    try {
      const response = await axios.post('http://192.168.173.161:8081/send_mail', {
        sender: 'ajaychelliah842005@gmail.com',
        to: 'ajay8425p@gmail.com',
        subject: 'Meeting Summary'
      });
      console.log('Email sent successfully:', response.data);
      setMessage('Email sent successfully');
    } catch (error) {
      console.error('Error sending email:', error);
      setMessage('Error sending email');
    }
  };

  return (
    <View style={styles.container}>
      <Button title="Start Recording" onPress={startRecording} />
      <Button title="Stop Recording" onPress={async () => {
        const uri = await stopRecording();
        sendAudio(uri);
      }} />
      <Button title="Transcribe Audio" onPress={transcribeAudio} />
      <Button title="Extract Details" onPress={extractDetails} />
      <Button title="Send Email" onPress={sendEmail} />
      <Text>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
});