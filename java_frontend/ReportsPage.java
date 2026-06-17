import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.net.*;

public class ReportsPage extends JFrame {

    JTextArea resultArea;

    public ReportsPage() {
        setTitle("Reports");
        setSize(600, 430);
        setLocationRelativeTo(null);
        setLayout(null);
        getContentPane().setBackground(new Color(245, 247, 250));

        JLabel title = new JLabel("Reports Panel", SwingConstants.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 24));
        title.setForeground(new Color(0, 70, 130));
        title.setBounds(100, 25, 400, 40);
        add(title);

        JButton pdf = new JButton("Open PDF Reports");
        pdf.setBounds(80, 100, 200, 45);
        styleButton(pdf);
        add(pdf);

        JButton graph = new JButton("Open Graph");
        graph.setBounds(320, 100, 200, 45);
        styleButton(graph);
        add(graph);

        JButton cleanup = new JButton("Cleanup Storage");
        cleanup.setBounds(200, 170, 200, 45);
        styleButton(cleanup);
        add(cleanup);

        resultArea = new JTextArea();
        resultArea.setEditable(false);
        resultArea.setFont(new Font("Segoe UI", Font.BOLD, 13));
        JScrollPane scroll = new JScrollPane(resultArea);
        scroll.setBounds(60, 240, 480, 100);
        add(scroll);

        pdf.addActionListener(e -> openFolder("../python_backend/pdf_reports"));
        graph.addActionListener(e -> openFile("../python_backend/graphs/video_result_graph.png"));
        cleanup.addActionListener(e -> {
            resultArea.setText(callGetApi("http://127.0.0.1:5000/cleanup_storage"));
        });

        setVisible(true);
    }

    void openFolder(String path) {
        try {
            File folder = new File(path);
            if (!folder.exists())
                folder.mkdirs();
            Desktop.getDesktop().open(folder);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Folder could not open");
        }
    }

    void openFile(String path) {
        try {
            File file = new File(path);
            if (!file.exists()) {
                JOptionPane.showMessageDialog(this, "File not found yet");
                return;
            }
            Desktop.getDesktop().open(file);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "File could not open");
        }
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