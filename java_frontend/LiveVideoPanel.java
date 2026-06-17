import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.net.URL;
import javax.imageio.ImageIO;

public class LiveVideoPanel extends JPanel {

    BufferedImage currentImage;
    String cameraId;

    public LiveVideoPanel(String cameraId) {
        this.cameraId = cameraId;
        setBackground(Color.WHITE);

        Thread thread = new Thread(() -> {
            while (true) {
                try {
                    URL url = new URL(
                            "http://127.0.0.1:5000/snapshot/"
                                    + cameraId
                                    + "?time="
                                    + System.currentTimeMillis());

                    BufferedImage newImage = ImageIO.read(url);

                    if (newImage != null) {
                        currentImage = newImage;
                    } else {
                        currentImage = null;
                    }

                    repaint();
                    Thread.sleep(300);

                } catch (Exception e) {
                    currentImage = null;
                    repaint();

                    try {
                        Thread.sleep(1000);
                    } catch (Exception ignored) {
                    }
                }
            }
        });

        thread.setDaemon(true);
        thread.start();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        if (currentImage != null) {
            g.drawImage(currentImage, 0, 0, getWidth(), getHeight(), null);
        } else {
            g.setColor(Color.WHITE);
            g.fillRect(0, 0, getWidth(), getHeight());

            g.setColor(Color.RED);
            g.setFont(new Font("Segoe UI", Font.BOLD, 16));
            g.drawString("Start " + cameraId, getWidth() / 2 - 55, getHeight() / 2);
        }

        g.setColor(Color.WHITE);
        g.setFont(new Font("Segoe UI", Font.BOLD, 14));
        g.drawString(cameraId, 10, 20);
    }
}