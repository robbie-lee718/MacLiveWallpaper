#!/usr/bin/env python3
"""
livewallpaper.py - play a looping video as a macOS desktop wallpaper.

Setup:
    pip3 install pyobjc-framework-Cocoa pyobjc-framework-AVFoundation pyobjc-framework-Quartz

Usage:
    python3 livewallpaper.py /path/to/video.mp4
"""

import os
import sys

from AppKit import (
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSApplicationDidChangeScreenParametersNotification,
    NSBackingStoreBuffered,
    NSColor,
    NSScreen,
    NSView,
    NSWindow,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorIgnoresCycle,
    NSWindowCollectionBehaviorStationary,
    NSWindowDidChangeOcclusionStateNotification,
    NSWindowOcclusionStateVisible,
    NSWindowStyleMaskBorderless,
    NSWorkspace,
    NSWorkspaceDidWakeNotification,
)
from AVFoundation import (
    AVLayerVideoGravityResizeAspectFill,
    AVPlayerItem,
    AVPlayerLayer,
    AVPlayerLooper,
    AVQueuePlayer,
)
from Foundation import NSNotificationCenter, NSOperationQueue, NSURL
from PyObjCTools import AppHelper
from Quartz import (
    CGWindowLevelForKey,
    kCALayerHeightSizable,
    kCALayerWidthSizable,
    kCGDesktopWindowLevelKey,
)


class WallpaperController:
    def __init__(self, path):
        self.url = NSURL.fileURLWithPath_(path)
        self.windows = []
        self.players = []
        self.loopers = []      # must be retained or looping stops
        self.observers = []    # (center, token) pairs
        self.screen_observer = None
        self.wake_observer = None

        self.build()

        # Rebuild when displays are added, removed, or change resolution
        self.screen_observer = NSNotificationCenter.defaultCenter().addObserverForName_object_queue_usingBlock_(
            NSApplicationDidChangeScreenParametersNotification,
            None,
            NSOperationQueue.mainQueue(),
            lambda note: self.build(),
        )

        # Resume after sleep (only for windows that are actually visible)
        ws_center = NSWorkspace.sharedWorkspace().notificationCenter()
        self.wake_observer = ws_center.addObserverForName_object_queue_usingBlock_(
            NSWorkspaceDidWakeNotification,
            None,
            NSOperationQueue.mainQueue(),
            lambda note: self.resume_visible(),
        )

    # -- helpers

    @staticmethod
    def is_visible(window):
        return bool(window.occlusionState() & NSWindowOcclusionStateVisible)

    def resume_visible(self):
        for window, player in zip(self.windows, self.players):
            if self.is_visible(window):
                player.play()

    def teardown(self):
        for center, token in self.observers:
            center.removeObserver_(token)
        self.observers = []
        for player in self.players:
            player.pause()
        for window in self.windows:
            window.orderOut_(None)
        self.windows = []
        self.players = []
        self.loopers = []

    # -- main

    def build(self):
        self.teardown()

        for screen in NSScreen.screens():
            frame = screen.frame()

            window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                frame, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False
            )
            window.setReleasedWhenClosed_(False)
            window.setFrame_display_(frame, True)

            # Desktop level: above the static wallpaper, below icons and app windows
            window.setLevel_(CGWindowLevelForKey(kCGDesktopWindowLevelKey))
            window.setCollectionBehavior_(
                NSWindowCollectionBehaviorCanJoinAllSpaces
                | NSWindowCollectionBehaviorStationary
                | NSWindowCollectionBehaviorIgnoresCycle
            )
            window.setOpaque_(True)
            window.setBackgroundColor_(NSColor.blackColor())
            window.setHasShadow_(False)
            window.setIgnoresMouseEvents_(True)  # clicks fall through

            player = AVQueuePlayer.alloc().init()
            player.setMuted_(True)
            item = AVPlayerItem.playerItemWithURL_(self.url)
            looper = AVPlayerLooper.playerLooperWithPlayer_templateItem_(player, item)

            view = NSView.alloc().initWithFrame_(frame)
            view.setWantsLayer_(True)
            layer = AVPlayerLayer.playerLayerWithPlayer_(player)
            layer.setFrame_(view.bounds())
            layer.setVideoGravity_(AVLayerVideoGravityResizeAspectFill)
            layer.setAutoresizingMask_(kCALayerWidthSizable | kCALayerHeightSizable)
            view.layer().addSublayer_(layer)

            window.setContentView_(view)
            window.orderBack_(None)
            player.play()

            # Pause when the window is fully covered (e.g. a fullscreen app)
            def on_occlusion(note, window=window, player=player):
                if self.is_visible(window):
                    player.play()
                else:
                    player.pause()

            center = NSNotificationCenter.defaultCenter()
            token = center.addObserverForName_object_queue_usingBlock_(
                NSWindowDidChangeOcclusionStateNotification,
                window,
                NSOperationQueue.mainQueue(),
                on_occlusion,
            )
            self.observers.append((center, token))

            self.windows.append(window)
            self.players.append(player)
            self.loopers.append(looper)


def main():
    if len(sys.argv) < 2:
        print("Usage: livewallpaper.py /path/to/video.mp4")
        sys.exit(1)

    path = os.path.abspath(os.path.expanduser(sys.argv[1]))
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        sys.exit(1)

    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)  # no Dock icon

    controller = WallpaperController(path)  # keep a reference alive
    AppHelper.runEventLoop(installInterrupt=True)  # Ctrl+C quits cleanly
    del controller


if __name__ == "__main__":
    main()