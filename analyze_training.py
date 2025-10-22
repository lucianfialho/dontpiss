#!/usr/bin/env python3
"""
Training Analytics - Analyze dog training progress over time
Reads detection logs and provides insights on training effectiveness
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path
import json


class TrainingAnalytics:
    """Analyze dog training progress from zone violation logs"""

    def __init__(self, log_file='logs/detections.csv'):
        self.log_file = Path(log_file)
        self.df = None

    def load_data(self):
        """Load detection logs"""
        if not self.log_file.exists():
            print(f"❌ Arquivo de log não encontrado: {self.log_file}")
            print("Execute o detector primeiro para gerar dados.")
            return False

        try:
            self.df = pd.read_csv(self.log_file)
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df['date'] = self.df['timestamp'].dt.date
            self.df['hour'] = self.df['timestamp'].dt.hour
            self.df['day_of_week'] = self.df['timestamp'].dt.day_name()

            print(f"✅ Carregados {len(self.df)} registros de detecção")
            return True

        except Exception as e:
            print(f"❌ Erro ao carregar logs: {e}")
            return False

    def get_summary_stats(self):
        """Get summary statistics"""
        if self.df is None or len(self.df) == 0:
            return None

        stats = {
            'total_violations': len(self.df),
            'first_detection': self.df['timestamp'].min(),
            'last_detection': self.df['timestamp'].max(),
            'days_monitored': (self.df['timestamp'].max() - self.df['timestamp'].min()).days + 1,
            'avg_violations_per_day': len(self.df) / max((self.df['timestamp'].max() - self.df['timestamp'].min()).days + 1, 1),
            'most_common_hour': self.df['hour'].mode()[0] if len(self.df) > 0 else None,
            'most_common_day': self.df['day_of_week'].mode()[0] if len(self.df) > 0 else None,
        }

        return stats

    def violations_per_day(self):
        """Count violations per day"""
        if self.df is None:
            return None

        daily = self.df.groupby('date').size().reset_index(name='violations')
        daily['date'] = pd.to_datetime(daily['date'])
        return daily

    def violations_per_hour(self):
        """Count violations per hour of day"""
        if self.df is None:
            return None

        hourly = self.df.groupby('hour').size().reset_index(name='violations')
        return hourly

    def violations_per_weekday(self):
        """Count violations per day of week"""
        if self.df is None:
            return None

        # Order by day of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly = self.df.groupby('day_of_week').size().reset_index(name='violations')
        weekly['day_of_week'] = pd.Categorical(weekly['day_of_week'], categories=day_order, ordered=True)
        weekly = weekly.sort_values('day_of_week')
        return weekly

    def calculate_trend(self):
        """Calculate training progress trend"""
        if self.df is None or len(self.df) < 2:
            return None

        daily = self.violations_per_day()

        # Calculate 7-day moving average
        daily['ma_7'] = daily['violations'].rolling(window=7, min_periods=1).mean()

        # Calculate trend (comparing first week vs last week)
        if len(daily) >= 7:
            first_week_avg = daily['violations'].head(7).mean()
            last_week_avg = daily['violations'].tail(7).mean()
            improvement = ((first_week_avg - last_week_avg) / first_week_avg * 100) if first_week_avg > 0 else 0
        else:
            improvement = None

        return {
            'daily_data': daily,
            'improvement_percentage': improvement
        }

    def print_report(self):
        """Print comprehensive training report"""
        if not self.load_data():
            return

        stats = self.get_summary_stats()

        print("\n" + "=" * 70)
        print("📊 RELATÓRIO DE TREINAMENTO - DontPiss")
        print("=" * 70)

        print("\n📈 ESTATÍSTICAS GERAIS")
        print("-" * 70)
        print(f"Total de violações: {stats['total_violations']}")
        print(f"Período monitorado: {stats['days_monitored']} dias")
        print(f"Primeira detecção: {stats['first_detection'].strftime('%d/%m/%Y %H:%M')}")
        print(f"Última detecção: {stats['last_detection'].strftime('%d/%m/%Y %H:%M')}")
        print(f"Média por dia: {stats['avg_violations_per_day']:.1f} violações")

        if stats['most_common_hour'] is not None:
            print(f"Horário mais comum: {stats['most_common_hour']:02d}:00")
        if stats['most_common_day'] is not None:
            print(f"Dia da semana mais comum: {stats['most_common_day']}")

        # Daily breakdown
        print("\n📅 VIOLAÇÕES POR DIA")
        print("-" * 70)
        daily = self.violations_per_day()
        for _, row in daily.tail(10).iterrows():
            date_str = row['date'].strftime('%d/%m/%Y')
            bar = '█' * int(row['violations'])
            print(f"{date_str}: {bar} ({int(row['violations'])})")

        # Hourly breakdown
        print("\n🕐 VIOLAÇÕES POR HORA DO DIA")
        print("-" * 70)
        hourly = self.violations_per_hour()
        for _, row in hourly.iterrows():
            hour_str = f"{int(row['hour']):02d}:00"
            bar = '█' * int(row['violations'] / max(hourly['violations']) * 30)
            print(f"{hour_str}: {bar} ({int(row['violations'])})")

        # Weekly breakdown
        print("\n📆 VIOLAÇÕES POR DIA DA SEMANA")
        print("-" * 70)
        weekly = self.violations_per_weekday()
        for _, row in weekly.iterrows():
            day_str = row['day_of_week'][:3]
            bar = '█' * int(row['violations'] / max(weekly['violations']) * 30)
            print(f"{day_str}: {bar} ({int(row['violations'])})")

        # Training progress
        print("\n🎯 PROGRESSO DO TREINAMENTO")
        print("-" * 70)
        trend = self.calculate_trend()
        if trend and trend['improvement_percentage'] is not None:
            improvement = trend['improvement_percentage']
            if improvement > 0:
                print(f"✅ Melhora de {improvement:.1f}% (primeira semana vs última semana)")
                print("   O cachorro está subindo MENOS no sofá! 🎉")
            elif improvement < 0:
                print(f"⚠️  Piora de {abs(improvement):.1f}% (primeira semana vs última semana)")
                print("   O cachorro está subindo MAIS no sofá...")
            else:
                print("➖ Sem mudança significativa")
        else:
            print("⏳ Dados insuficientes para calcular tendência (mínimo 7 dias)")

        # Recent activity
        print("\n🔥 ÚLTIMAS 5 DETECÇÕES")
        print("-" * 70)
        for _, row in self.df.tail(5).iterrows():
            time_str = row['timestamp'].strftime('%d/%m/%Y %H:%M:%S')
            print(f"  • {time_str}")

        print("\n" + "=" * 70)

    def create_charts(self, output_dir='analytics'):
        """Create visualization charts"""
        if self.df is None:
            return

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Chart 1: Violations per day with trend
        plt.figure(figsize=(12, 6))
        daily = self.violations_per_day()
        daily['ma_7'] = daily['violations'].rolling(window=7, min_periods=1).mean()

        plt.subplot(2, 2, 1)
        plt.bar(daily['date'], daily['violations'], alpha=0.6, label='Violações diárias')
        plt.plot(daily['date'], daily['ma_7'], 'r-', linewidth=2, label='Média móvel (7 dias)')
        plt.xlabel('Data')
        plt.ylabel('Número de violações')
        plt.title('Violações ao longo do tempo')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Chart 2: Violations per hour
        plt.subplot(2, 2, 2)
        hourly = self.violations_per_hour()
        plt.bar(hourly['hour'], hourly['violations'], color='orange', alpha=0.7)
        plt.xlabel('Hora do dia')
        plt.ylabel('Número de violações')
        plt.title('Violações por hora do dia')
        plt.xticks(range(0, 24, 2))
        plt.grid(True, alpha=0.3)

        # Chart 3: Violations per weekday
        plt.subplot(2, 2, 3)
        weekly = self.violations_per_weekday()
        plt.bar(range(len(weekly)), weekly['violations'], color='green', alpha=0.7)
        plt.xlabel('Dia da semana')
        plt.ylabel('Número de violações')
        plt.title('Violações por dia da semana')
        plt.xticks(range(len(weekly)), [d[:3] for d in weekly['day_of_week']])
        plt.grid(True, alpha=0.3)

        # Chart 4: Cumulative violations
        plt.subplot(2, 2, 4)
        daily['cumulative'] = daily['violations'].cumsum()
        plt.plot(daily['date'], daily['cumulative'], 'b-', linewidth=2)
        plt.fill_between(daily['date'], daily['cumulative'], alpha=0.3)
        plt.xlabel('Data')
        plt.ylabel('Total acumulado')
        plt.title('Violações acumuladas')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        chart_file = output_path / 'training_progress.png'
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        print(f"\n📊 Gráficos salvos em: {chart_file}")
        plt.close()

    def export_summary(self, output_file='analytics/training_summary.json'):
        """Export summary statistics to JSON"""
        if self.df is None:
            return

        stats = self.get_summary_stats()
        trend = self.calculate_trend()

        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_violations': int(stats['total_violations']),
            'days_monitored': int(stats['days_monitored']),
            'avg_violations_per_day': float(stats['avg_violations_per_day']),
            'first_detection': stats['first_detection'].isoformat(),
            'last_detection': stats['last_detection'].isoformat(),
            'most_common_hour': int(stats['most_common_hour']) if stats['most_common_hour'] is not None else None,
            'most_common_day': stats['most_common_day'],
            'improvement_percentage': float(trend['improvement_percentage']) if trend and trend['improvement_percentage'] is not None else None,
            'daily_violations': self.violations_per_day().to_dict('records')
        }

        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"📄 Resumo exportado para: {output_path}")


def main():
    """Main entry point"""
    import sys

    analytics = TrainingAnalytics()

    # Print text report
    analytics.print_report()

    # Ask if user wants charts
    if len(sys.argv) > 1 and sys.argv[1] == '--charts':
        print("\n📊 Gerando gráficos...")
        analytics.create_charts()
        analytics.export_summary()
        print("\n✅ Análise completa!")
        print("\nArquivos gerados:")
        print("  - analytics/training_progress.png (gráficos)")
        print("  - analytics/training_summary.json (dados)")
    else:
        print("\n💡 Dica: Execute com --charts para gerar gráficos visuais:")
        print("   python analyze_training.py --charts")


if __name__ == "__main__":
    main()
