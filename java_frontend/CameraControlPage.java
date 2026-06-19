import javax.swing.*;
import java.awt.*;
import java.io.File;

public class CameraControlPage extends JFrame {

    DashboardPage dashboard;
    JTextField cam1, cam2, cam3, cam4;
    JTextArea resultArea;

    public CameraControlPage(DashboardPage dashboard) {
        this.dashboard = dashboard;

        setTitle("Camera Control");
        setSize(720, 560);
        setLocationRelativeTo(null);
        setLayout(null);
        getContentPane().setBackground(new Color(245, 247, 250));

        JLabel title = new JLabel("Camera Control Panel", SwingConstants.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 24));
        title.setForeground(new Color(0, 70, 130));
        title.setBounds(80, 20, 560, 40);
        add(title);

        cam1 = addCameraRow("CAM_1", 80, "0");
        cam2 = addCameraRow("CAM_2", 140, "http://192.168.1.10:8080/video");
        cam3 = addCameraRow("CAM_3", 200, "rtsp://username:password@192.168.1.100:554/stream1");
        cam4 = addCameraRow("CAM_4", 260, "videos/test.mp4");

        JButton detectSavedFrame = new JButton("Detect Saved Frame");
        detectSavedFrame.setBounds(250, 315, 200, 35);
        styleButton(detectSavedFrame);
        add(detectSavedFrame);

        JButton startAll = new JButton("Start All Cameras");
        startAll.setBounds(120, 370, 200, 40);
        styleButton(startAll);
        add(startAll);

        JButton stopAll = new JButton("Stop All Cameras");
        stopAll.setBounds(380, 370, 200, 40);
        styleButton(stopAll);
        add(stopAll);

        resultArea = new JTextArea("Camera System Ready");
        resultArea.setEditable(false);
        resultArea.setFont(new Font("Segoe UI", Font.BOLD, 13));
        resultArea.setLineWrap(true);
        resultArea.setWrapStyleWord(true);

        JScrollPane scroll = new JScrollPane(resultArea);
        scroll.setBounds(60, 430, 600, 80);
        add(scroll);

        detectSavedFrame.addActionListener(e -> detectSavedFrame());
        startAll.addActionListener(e -> startAll());
        stopAll.addActionListener(e -> stopAll());

        setVisible(true);
    }

    JTextField addCameraRow(String cameraId, int y, String defaultSource) {
        JLabel label = new JLabel(cameraId);
        label.setBounds(50, y, 70, 35);
        label.setFont(new Font("Segoe UI", Font.BOLD, 14));
        add(label);

        JTextField source = new JTextField(defaultSource);
        source.setBounds(120, y, 280, 35);
        add(source);

        JButton start = new JButton("Start");
        start.setBounds(420, y, 90, 35);
        styleButton(start);
        add(start);

        JButton stop = new JButton("Stop");
        stop.setBounds(530, y, 90, 35);
        styleButton(stop);
        add(stop);

        start.addActionListener(e -> {
            String response = dashboard.callPostApi(
                    "http://127.0.0.1:5000/start_camera",
                    "camera_id=" + dashboard.encode(cameraId) +
                            "&camera_url=" + dashboard.encode(source.getText().trim()));

            resultArea.setText(cameraId + " Started");
            dashboard.updateCameraStatus();
        });

        stop.addActionListener(e -> {
            String response = dashboard.callPostApi(
                    "http://127.0.0.1:5000/stop_camera",
                    "camera_id=" + dashboard.encode(cameraId));

            resultArea.setText(cameraId + " Stopped");
            dashboard.updateCameraStatus();
        });

        return source;
    }

    void startAll() {
        String data = "cam1=" + dashboard.encode(cam1.getText().trim()) +
                "&cam2=" + dashboard.encode(cam2.getText().trim()) +
                "&cam3=" + dashboard.encode(cam3.getText().trim()) +
                "&cam4=" + dashboard.encode(cam4.getText().trim());

        dashboard.callPostApi("http://127.0.0.1:5000/start_multi_camera", data);

        resultArea.setText("Camera Monitoring Started");
        dashboard.updateCameraStatus();
    }

    void stopAll() {
        dashboard.callPostApi("http://127.0.0.1:5000/stop_multi_camera", "");

        resultArea.setText("Camera Monitoring Stopped");
        dashboard.updateCameraStatus();
    }

    void detectSavedFrame() {
        String[] options = {
                "Temporary Camera Frames",
                "Captured Frames",
                "Tiger Screenshots"
        };

        String choice = (String) JOptionPane.showInputDialog(
                this,
                "Choose frame folder:",
                "Manual Detection",
                JOptionPane.PLAIN_MESSAGE,
                null,
                options,
                options[0]);

        if (choice == null)
            return;

        String folderPath;

        if (choice.equals("Temporary Camera Frames")) {
            folderPath = "../python_backend/temp_frames";
        } else if (choice.equals("Captured Frames")) {
            folderPath = "../python_backend/captured_frames";
        } else {
            folderPath = "../python_backend/saved_tigers";
        }

        JFileChooser chooser = new JFileChooser(folderPath);
        chooser.setDialogTitle("Select frame to detect");

        int option = chooser.showOpenDialog(this);

        if (option == JFileChooser.APPROVE_OPTION) {
            File selectedFrame = chooser.getSelectedFile();

            resultArea.setText("Checking selected frame...");

            String response = ApiClient.sendFile("detect_photo", selectedFrame);

            resultArea.setText(response);
        }
    }

    void styleButton(JButton button) {
        button.setBackground(Color.WHITE);
        button.setForeground(Color.BLACK);
        button.setOpaque(true);
        button.setContentAreaFilled(true);
        button.setBorderPainted(true);
        button.setFocusPainted(false);
        button.setFont(new Font("Segoe UI", Font.BOLD, 13));
        button.setBorder(BorderFactory.createLineBorder(new Color(0, 105, 180), 2));
    }
}