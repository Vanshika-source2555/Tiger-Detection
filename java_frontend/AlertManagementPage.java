import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.net.*;

public class AlertManagementPage extends JFrame {

    JTextArea alertArea;

    public AlertManagementPage() {
        setTitle("Alert Management");
        setSize(750, 500);
        setLocationRelativeTo(null);
        setLayout(null);
        getContentPane().setBackground(new Color(245, 247, 250));

        JLabel title = new JLabel("Tiger Alert Management", SwingConstants.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 24));
        title.setForeground(new Color(0, 70, 130));
        title.setBounds(100, 20, 550, 40);
        add(title);

        alertArea = new JTextArea();
        alertArea.setEditable(false);
        alertArea.setFont(new Font("Segoe UI", Font.BOLD, 13));

        JScrollPane scroll = new JScrollPane(alertArea);
        scroll.setBounds(50, 80, 640, 280);
        add(scroll);

        JButton refresh = new JButton("Refresh Alerts");
        refresh.setBounds(150, 385, 180, 40);
        styleButton(refresh);
        add(refresh);

        JButton clear = new JButton("Clear Alerts");
        clear.setBounds(390, 385, 180, 40);
        styleButton(clear);
        add(clear);

        refresh.addActionListener(e -> loadAlerts());

        clear.addActionListener(e -> {
            String response = callPostApi("http://127.0.0.1:5000/clear_alerts", "");
            alertArea.setText(response);
        });

        loadAlerts();
        setVisible(true);
    }

    void loadAlerts() {
        alertArea.setText(callGetApi("http://127.0.0.1:5000/alerts"));
    }

    String callGetApi(String apiUrl) {
        try {
            URL url = new URL(apiUrl);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");

            BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            StringBuilder response = new StringBuilder();
            String line;

            while ((line = br.readLine()) != null)
                response.append(line).append("\n");

            br.close();
            return response.toString();
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    String callPostApi(String apiUrl, String data) {
        try {
            URL url = new URL(apiUrl);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();

            conn.setRequestMethod("POST");
            conn.setDoOutput(true);

            OutputStream os = conn.getOutputStream();
            os.write(data.getBytes());
            os.flush();
            os.close();

            BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            StringBuilder response = new StringBuilder();
            String line;

            while ((line = br.readLine()) != null)
                response.append(line).append("\n");

            br.close();
            return response.toString();
        } catch (Exception e) {
            return "Error: " + e.getMessage();
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

        button.setBorder(
                BorderFactory.createLineBorder(
                        new Color(0, 105, 180),
                        2));
    }
}