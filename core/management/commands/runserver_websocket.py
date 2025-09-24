"""
Management command to start the server with WebSocket support using Daphne.
This ensures that WebSocket connections work properly for the chat system.
"""
from django.core.management.base import BaseCommand
import subprocess
import sys
import os


class Command(BaseCommand):
    help = 'Start the Django server with WebSocket support using Daphne'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            default='127.0.0.1',
            help='Host to bind to (default: 127.0.0.1)'
        )
        parser.add_argument(
            '--port',
            default='8080',
            help='Port to bind to (default: 8080)'
        )
        parser.add_argument(
            '--reload',
            action='store_true',
            help='Enable auto-reload on code changes'
        )

    def handle(self, *args, **options):
        host = options['host']
        port = options['port']
        reload = options['reload']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🚀 Starting Django server with WebSocket support...\n'
                f'📍 Host: {host}\n'
                f'🔌 Port: {port}\n'
                f'🔄 Auto-reload: {"Enabled" if reload else "Disabled"}\n'
                f'🌐 WebSocket URL: ws://{host}:{port}/ws/chat/room/ROOM_ID/\n'
                f'📱 Access URL: http://{host}:{port}/\n'
            )
        )
        
        # Build daphne command
        cmd = [
            'daphne',
            '-b', host,
            '-p', port,
            'project_manager.asgi:application'
        ]
        
        if reload:
            cmd.append('--reload')
        
        try:
            # Start the server
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to start server: {e}')
            )
            sys.exit(1)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n🛑 Server stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Unexpected error: {e}')
            )
            sys.exit(1)
