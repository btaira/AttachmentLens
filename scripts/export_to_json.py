#!/usr/bin/env python3
"""
Export AttachmentLens database to JSON for backup or static hosting.
Usage: python scripts/export_to_json.py [output_file.json]
"""

import sqlite3
import json
import sys
from datetime import datetime

def export_database(output_file='posts.json'):
    """Export posts and insights to JSON."""
    try:
        conn = sqlite3.connect('posts.db')
        conn.row_factory = sqlite3.Row

        posts = [dict(r) for r in conn.execute(
            'SELECT * FROM posts ORDER BY id DESC'
        ).fetchall()]

        insights = [dict(r) for r in conn.execute(
            'SELECT * FROM insights ORDER BY id DESC'
        ).fetchall()]

        ai_analyses = [dict(r) for r in conn.execute(
            'SELECT * FROM ai_analyses ORDER BY id DESC'
        ).fetchall()]

        export = {
            'exported_at': datetime.now().isoformat(),
            'posts': posts,
            'insights': insights,
            'ai_analyses': ai_analyses,
            'stats': {
                'total_posts': len(posts),
                'total_insights': len(insights),
                'total_analyses': len(ai_analyses),
            }
        }

        with open(output_file, 'w') as f:
            json.dump(export, f, indent=2)

        print(f"✅ Exported to {output_file}")
        print(f"   Posts: {len(posts)}")
        print(f"   Insights: {len(insights)}")
        print(f"   Analyses: {len(ai_analyses)}")

        conn.close()
    except FileNotFoundError:
        print("❌ Error: posts.db not found. Run the app first to create it.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    output = sys.argv[1] if len(sys.argv) > 1 else 'posts.json'
    export_database(output)
