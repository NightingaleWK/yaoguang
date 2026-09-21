using System;
using System.Drawing;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;

internal static class Native {
    [DllImport("user32.dll")] internal static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] internal static extern bool GetLastInputInfo(ref LastInputInfo i);
    [DllImport("user32.dll")] internal static extern bool LockWorkStation();
    [StructLayout(LayoutKind.Sequential)] internal struct LastInputInfo { public uint cbSize; public uint dwTime; }
    internal static uint LastInput() { var i = new LastInputInfo { cbSize = (uint)Marshal.SizeOf(typeof(LastInputInfo)) }; return GetLastInputInfo(ref i) ? i.dwTime : 0; }
    internal static void Display(int level) { SendMessage(new IntPtr(0xffff), 0x0112, new IntPtr(0xF170), new IntPtr(level)); }
}

internal sealed class Settings { public bool AutoLockEnabled { get; set; } public int IdleSeconds { get; set; } public Settings(){AutoLockEnabled=true;IdleSeconds=60;} }

internal sealed class MainForm : Form {
    readonly string dir = AppDomain.CurrentDomain.BaseDirectory, logPath, settingsPath; readonly Label status; readonly CheckBox auto; readonly NumericUpDown seconds; readonly Button mode; readonly Timer timer;
    Settings config; string state = "Ready"; uint baseline, wake; bool locked;
    MainForm() {
        logPath = Path.Combine(dir, "yaoguang.log"); settingsPath = Path.Combine(dir, "settings.json"); Log("启动 Yaoguang EXE"); config = Load();
        Text = "Yaoguang 下班模式"; ClientSize = new Size(430, 330); StartPosition = FormStartPosition.CenterScreen; FormBorderStyle = FormBorderStyle.FixedDialog; MaximizeBox = false;
        Controls.Add(Label("Yaoguang 下班模式", 24, 18, 16, true)); status = Label("当前状态：正常运行", 26, 62, 11, true); Controls.Add(status);
        auto = new CheckBox { Text = "启用无操作自动锁屏", Checked = config.AutoLockEnabled, Location = new Point(28, 105), AutoSize = true }; Controls.Add(auto);
        Controls.Add(Label("无操作时间（秒）：", 28, 140, 10, false)); seconds = new NumericUpDown { Minimum = 10, Maximum = 86400, Value = Math.Max(10, Math.Min(86400, config.IdleSeconds)), Location = new Point(160, 136), Width = 90 }; Controls.Add(seconds);
        var hint = Label("关闭显示器后，移动鼠标或按键盘会唤醒屏幕。", 28, 174, 9, false); hint.ForeColor = Color.DimGray; Controls.Add(hint);
        mode = new Button { Text = "进入下班模式", Location = new Point(28, 212), Size = new Size(170, 42) }; mode.Click += Toggle; Controls.Add(mode);
        var restore = new Button { Text = "恢复显示器", Location = new Point(210, 212), Size = new Size(170, 42) }; restore.Click += (s,e) => ExitMode(); Controls.Add(restore);
        var save = new Button { Text = "保存设置", Location = new Point(28, 268), Size = new Size(110, 30) }; save.Click += (s,e) => { Save(); MessageBox.Show("设置已保存。", "Yaoguang"); }; Controls.Add(save);
        timer = new Timer { Interval = 250 }; timer.Tick += Tick; FormClosing += (s,e) => { if (state != "Ready" && !locked) Native.Display(-1); timer.Stop(); Log("退出"); };
    }
    static Label Label(string text,int x,int y,float size,bool bold) { return new Label { Text=text, Location=new Point(x,y), AutoSize=true, Font=new Font("Microsoft YaHei UI",size,bold?FontStyle.Bold:FontStyle.Regular) }; }
    static MainForm Create() { try { return new MainForm(); } catch(Exception e) { File.AppendAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory,"yaoguang.log"), DateTime.Now+" CREATE ERROR "+e+Environment.NewLine); throw; } }
    Settings Load() { var s=new Settings(); try { if(File.Exists(settingsPath)){foreach(var line in File.ReadAllLines(settingsPath)){if(line.Contains("AutoLockEnabled"))s.AutoLockEnabled=!line.Contains("false");if(line.Contains("IdleSeconds")){int n;if(int.TryParse(line.Split(':')[1].Trim(' ',',','"'),out n))s.IdleSeconds=n;}}} } catch(Exception e){Log("配置读取失败: "+e.Message);} return s; }
    void Save() { config.AutoLockEnabled=auto.Checked; config.IdleSeconds=(int)seconds.Value; File.WriteAllText(settingsPath,"{\r\n  \"AutoLockEnabled\": "+config.AutoLockEnabled.ToString().ToLower()+",\r\n  \"IdleSeconds\": "+config.IdleSeconds+"\r\n}"); Log("保存设置"); }
    void Log(string s) { try { File.AppendAllText(logPath, DateTime.Now.ToString("s")+" "+s+Environment.NewLine); } catch {} }
    void Toggle(object sender,EventArgs e) { if(state=="Ready"){Save();baseline=Native.LastInput();Native.Display(2);state="Waiting";timer.Start();RefreshUi();Log("进入下班模式");} else ExitMode(); }
    void ExitMode() { Native.Display(-1);timer.Stop();state="Ready";locked=false;RefreshUi();Log("恢复显示器"); }
    void Tick(object sender,EventArgs e) { if(state=="Waiting"){uint n=Native.LastInput();if(n!=0&&n!=baseline){wake=n;state=auto.Checked?"Counting":"Ready";RefreshUi();}} else if(state=="Counting"){uint n=Native.LastInput();if(n!=wake){wake=n;RefreshUi();return;}if((uint)(Environment.TickCount-wake)>=(uint)seconds.Value*1000){if(Native.LockWorkStation()){locked=true;state="Locked";RefreshUi();Log("自动锁屏");}}else RefreshUi();} }
    void RefreshUi(){if(state=="Ready"){status.Text="当前状态：正常运行";mode.Text="进入下班模式";}else if(state=="Waiting"){status.Text="当前状态：显示器已关闭，等待输入";mode.Text="退出下班模式";}else if(state=="Counting"){int left=Math.Max(0,(int)seconds.Value-(int)((uint)(Environment.TickCount-wake)/1000));status.Text="当前状态：已唤醒，"+left+" 秒后自动锁屏";mode.Text="退出下班模式";}else{status.Text="当前状态：已锁屏";mode.Text="退出下班模式";}}
    [STAThread] static void Main(){try{Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);Application.Run(Create());}catch(Exception e){MessageBox.Show("Yaoguang 启动失败：\n"+e.Message+"\n\n详细信息已写入 yaoguang.log","Yaoguang",MessageBoxButtons.OK,MessageBoxIcon.Error);}}
}
