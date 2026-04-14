using BlinkReminder.Native.ViewModels;
using Microsoft.UI.Xaml;

namespace BlinkReminder.Native;

public sealed partial class MainWindow : Window
{
    public MainViewModel ViewModel { get; }

    public MainWindow()
    {
        ViewModel = new MainViewModel();
        Resources["CardStyle"] = BuildResources.CardStyle();
        Resources["CardTitleStyle"] = BuildResources.CardTitleStyle();
        Resources["CardValueStyle"] = BuildResources.CardValueStyle();
        Resources["CardNoteStyle"] = BuildResources.CardNoteStyle();
        Resources["SectionTitleStyle"] = BuildResources.SectionTitleStyle();
        Resources["BulletStyle"] = BuildResources.BulletStyle();
        InitializeComponent();
    }
}
