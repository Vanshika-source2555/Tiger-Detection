import javax.swing.*;
import java.awt.*;
import java.io.File;

import javafx.application.Platform;
import javafx.embed.swing.JFXPanel;
import javafx.scene.Scene;
import javafx.scene.input.KeyCode;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.media.Media;
import javafx.scene.media.MediaPlayer;
import javafx.scene.media.MediaView;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.Slider;
import javafx.util.Duration;

public class FullScreenPreview extends JFrame {

    MediaPlayer mediaPlayer;
    boolean isPlaying = true;

    public FullScreenPreview(File file) {

        setTitle("Full Screen Preview");
        setExtendedState(JFrame.MAXIMIZED_BOTH);
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        setLayout(new BorderLayout());

        String fileName = file.getName().toLowerCase();

        if (fileName.endsWith(".mp4") || fileName.endsWith(".avi") || fileName.endsWith(".mov")) {
            playVideo(file);
        } else {
            showImage(file);
        }

        setVisible(true);
    }

    void showImage(File file) {

        JLabel imageLabel = new JLabel("", SwingConstants.CENTER);
        imageLabel.setBackground(Color.BLACK);
        imageLabel.setOpaque(true);

        try {
            ImageIcon icon = new ImageIcon(file.getAbsolutePath());
            Dimension screen = Toolkit.getDefaultToolkit().getScreenSize();

            Image img = icon.getImage().getScaledInstance(
                    screen.width,
                    screen.height,
                    Image.SCALE_SMOOTH);

            imageLabel.setIcon(new ImageIcon(img));

        } catch (Exception e) {
            imageLabel.setText("Preview not available");
            imageLabel.setForeground(Color.WHITE);
            imageLabel.setFont(new Font("Segoe UI", Font.BOLD, 30));
        }

        JButton closeButton = new JButton("Close Preview");
        closeButton.setFont(new Font("Segoe UI", Font.BOLD, 18));
        closeButton.addActionListener(e -> dispose());

        add(imageLabel, BorderLayout.CENTER);
        add(closeButton, BorderLayout.SOUTH);
    }

    void playVideo(File file) {

        JFXPanel fxPanel = new JFXPanel();
        add(fxPanel, BorderLayout.CENTER);

        Platform.runLater(() -> {

            try {
                Media media = new Media(file.toURI().toString());
                mediaPlayer = new MediaPlayer(media);
                mediaPlayer.setAutoPlay(true);

                MediaView mediaView = new MediaView(mediaPlayer);

                Dimension screen = Toolkit.getDefaultToolkit().getScreenSize();

                mediaView.setFitWidth(screen.width);
                mediaView.setFitHeight(screen.height - 180);
                mediaView.setPreserveRatio(true);

                StackPane videoPane = new StackPane(mediaView);
                videoPane.setStyle("-fx-background-color: black;");

                Button playPause = new Button("Pause");
                Button back = new Button("Back 10s");
                Button forward = new Button("Forward 10s");
                Button close = new Button("Close");
                Button full = new Button("Full Screen");

                Slider progress = new Slider();
                progress.setMin(0);
                progress.setPrefWidth(350);

                Slider volume = new Slider(0, 100, 70);
                volume.setPrefWidth(120);

                Label progressLabel = new Label("Progress");
                progressLabel.setStyle("-fx-text-fill: white;");

                Label volumeLabel = new Label("Volume");
                volumeLabel.setStyle("-fx-text-fill: white;");

                Label timeLabel = new Label("00:00 / 00:00");
                timeLabel.setStyle("-fx-text-fill: white; -fx-font-weight: bold;");

                mediaPlayer.setVolume(0.7);

                HBox controls = new HBox(10);
                controls.setStyle("-fx-background-color: #111111; -fx-padding: 12;");

                controls.getChildren().addAll(
                        playPause,
                        back,
                        forward,
                        progressLabel,
                        progress,
                        timeLabel,
                        volumeLabel,
                        volume,
                        full,
                        close);

                BorderPane root = new BorderPane();
                root.setCenter(videoPane);
                root.setBottom(controls);
                root.setStyle("-fx-background-color: black;");

                Scene scene = new Scene(root, screen.width, screen.height);

                fxPanel.setScene(scene);

                mediaPlayer.setOnReady(() -> {
                    progress.setMax(mediaPlayer.getTotalDuration().toSeconds());
                    mediaPlayer.play();
                });

                mediaPlayer.currentTimeProperty().addListener((obs, oldTime, newTime) -> {
                    if (!progress.isValueChanging()) {
                        progress.setValue(newTime.toSeconds());
                    }

                    String current = formatTime(newTime);
                    String total = formatTime(mediaPlayer.getTotalDuration());
                    timeLabel.setText(current + " / " + total);
                });

                progress.valueChangingProperty().addListener((obs, wasChanging, isChanging) -> {
                    if (!isChanging) {
                        mediaPlayer.seek(Duration.seconds(progress.getValue()));
                    }
                });

                progress.setOnMouseReleased(e -> {
                    mediaPlayer.seek(Duration.seconds(progress.getValue()));
                });

                playPause.setOnAction(e -> {
                    if (isPlaying) {
                        mediaPlayer.pause();
                        playPause.setText("Play");
                        isPlaying = false;
                    } else {
                        mediaPlayer.play();
                        playPause.setText("Pause");
                        isPlaying = true;
                    }
                });

                back.setOnAction(e -> {
                    Duration current = mediaPlayer.getCurrentTime();
                    mediaPlayer.seek(current.subtract(Duration.seconds(10)));
                });

                forward.setOnAction(e -> {
                    Duration current = mediaPlayer.getCurrentTime();
                    mediaPlayer.seek(current.add(Duration.seconds(10)));
                });

                volume.valueProperty().addListener((obs, oldVal, newVal) -> {
                    mediaPlayer.setVolume(newVal.doubleValue() / 100);
                });

                full.setOnAction(e -> {
                    setExtendedState(JFrame.MAXIMIZED_BOTH);
                });

                close.setOnAction(e -> {
                    mediaPlayer.stop();
                    dispose();
                });

                scene.setOnKeyPressed(e -> {
                    if (e.getCode() == KeyCode.ESCAPE) {
                        mediaPlayer.stop();
                        dispose();
                    }

                    if (e.getCode() == KeyCode.SPACE) {
                        if (isPlaying) {
                            mediaPlayer.pause();
                            playPause.setText("Play");
                            isPlaying = false;
                        } else {
                            mediaPlayer.play();
                            playPause.setText("Pause");
                            isPlaying = true;
                        }
                    }
                });

            } catch (Exception e) {
                e.printStackTrace();
            }

        });
    }

    String formatTime(Duration duration) {

        int totalSeconds = (int) duration.toSeconds();

        int minutes = totalSeconds / 60;
        int seconds = totalSeconds % 60;

        return String.format("%02d:%02d", minutes, seconds);
    }

    @Override
    public void dispose() {
        if (mediaPlayer != null) {
            mediaPlayer.stop();
        }
        super.dispose();
    }
}