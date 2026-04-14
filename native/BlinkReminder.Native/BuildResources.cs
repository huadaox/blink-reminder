using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Windows.UI;

namespace BlinkReminder.Native;

internal static class BuildResources
{
    public static Style CardStyle()
    {
        var style = new Style(typeof(Border));
        style.Setters.Add(new Setter(Border.BackgroundProperty, new SolidColorBrush(Color.FromArgb(255, 16, 27, 44))));
        style.Setters.Add(new Setter(Border.BorderBrushProperty, new SolidColorBrush(Color.FromArgb(255, 28, 48, 72))));
        style.Setters.Add(new Setter(Border.BorderThicknessProperty, new Thickness(1)));
        style.Setters.Add(new Setter(Border.CornerRadiusProperty, new CornerRadius(20)));
        style.Setters.Add(new Setter(Border.PaddingProperty, new Thickness(18, 16, 18, 16)));
        return style;
    }

    public static Style CardTitleStyle() => BuildTextStyle(12, Color.FromArgb(255, 145, 167, 190), false);
    public static Style CardValueStyle() => BuildTextStyle(30, Color.FromArgb(255, 244, 248, 252), true);
    public static Style CardNoteStyle() => BuildTextStyle(12, Color.FromArgb(255, 142, 165, 188), false);
    public static Style SectionTitleStyle() => BuildTextStyle(15, Color.FromArgb(255, 244, 248, 252), true);
    public static Style BulletStyle() => BuildTextStyle(14, Color.FromArgb(255, 142, 165, 188), false);

    private static Style BuildTextStyle(double fontSize, Color color, bool semibold)
    {
        var style = new Style(typeof(TextBlock));
        style.Setters.Add(new Setter(TextBlock.FontSizeProperty, fontSize));
        style.Setters.Add(new Setter(TextBlock.ForegroundProperty, new SolidColorBrush(color)));
        style.Setters.Add(new Setter(TextBlock.TextWrappingProperty, TextWrapping.Wrap));
        if (semibold)
        {
            style.Setters.Add(new Setter(TextBlock.FontWeightProperty, Windows.UI.Text.FontWeights.SemiBold));
        }

        return style;
    }
}
