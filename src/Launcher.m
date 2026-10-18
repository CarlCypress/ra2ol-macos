#import <Cocoa/Cocoa.h>

@interface RA2Launcher : NSObject <NSApplicationDelegate>
@property NSWindow *window;
@property NSTextField *status;
@property NSTask *task;
@property NSTask *stopTask;
@property BOOL stopping;
@property NSString *base;
@end

@implementation RA2Launcher
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
    self.window = [[NSWindow alloc] initWithContentRect:NSMakeRect(0,0,420,145)
        styleMask:NSWindowStyleMaskTitled|NSWindowStyleMaskClosable
        backing:NSBackingStoreBuffered defer:NO];
    self.window.title = @"红警战网";
    [self.window center];
    self.status = [NSTextField wrappingLabelWithString:@"正在启动战网安装程序…"];
    self.status.frame = NSMakeRect(24,50,372,65);
    [self.window.contentView addSubview:self.status];
    NSButton *stop = [NSButton buttonWithTitle:@"强制结束战网和游戏" target:self action:@selector(stopGame:)];
    stop.frame = NSMakeRect(24,12,220,30);
    [self.window.contentView addSubview:stop];
    [self.window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];

    NSDictionary *settings = [NSDictionary dictionaryWithContentsOfFile:
        [[NSBundle mainBundle] pathForResource:@"settings" ofType:@"plist"]];
    NSString *base = [(settings[@"baseDirectory"] ?: @"~/RA2OLMac") stringByExpandingTildeInPath];
    self.base = base;
    NSString *prefix = [base stringByAppendingPathComponent:@"prefix"];
    NSString *game = [prefix stringByAppendingPathComponent:@"drive_c/RA2OL/HTPlatform.exe"];
    BOOL installed = [[NSFileManager defaultManager] fileExistsAtPath:game];
    NSString *program = installed ? game : [base stringByAppendingPathComponent:@"installers/ra2ol-legacy-setup.exe"];
    if (![[NSFileManager defaultManager] fileExistsAtPath:program]) {
        self.status.stringValue = @"尚未准备运行环境。请按项目 README 完成 setup。";
        return;
    }
    NSMutableDictionary *env = [[[NSProcessInfo processInfo] environment] mutableCopy];
    env[@"WINEPREFIX"] = prefix;
    env[@"LANG"] = @"zh_CN.GBK";
    env[@"LC_ALL"] = @"zh_CN.GBK";
    env[@"WINEDEBUG"] = @"-all";
    env[@"MVK_CONFIG_LOG_LEVEL"] = @"0";
    NSString *wineRuntime = [base stringByAppendingPathComponent:@"runtime/Wine Stable.app/Contents/Resources/wine"];
    env[@"WINELOADER"] = [wineRuntime stringByAppendingPathComponent:@"bin/wine"];
    NSString *gst = [base stringByAppendingPathComponent:@"runtime/GStreamer.framework/Versions/1.0"];
    env[@"DYLD_FALLBACK_LIBRARY_PATH"] = [NSString stringWithFormat:@"%@/lib:%@/lib:/usr/local/lib:/usr/lib", wineRuntime, gst];
    [env removeObjectForKey:@"DYLD_LIBRARY_PATH"];
    env[@"DYLD_INSERT_LIBRARIES"] = [[NSBundle mainBundle] pathForResource:@"ControlAsAlt" ofType:@"dylib"];
    env[@"GST_PLUGIN_SYSTEM_PATH"] = [gst stringByAppendingPathComponent:@"lib/gstreamer-1.0"];
    env[@"GST_PLUGIN_SCANNER"] = [gst stringByAppendingPathComponent:@"libexec/gstreamer-1.0/gst-plugin-scanner"];
    env[@"GST_REGISTRY"] = [base stringByAppendingPathComponent:@"gstreamer-registry.bin"];
    self.task = [[NSTask alloc] init];
    self.task.executableURL = [NSURL fileURLWithPath:env[@"WINELOADER"]];
    self.task.arguments = @[program];
    self.task.environment = env;
    self.task.currentDirectoryURL = [NSURL fileURLWithPath:installed ? [game stringByDeletingLastPathComponent] : base];
    NSString *logName = [NSString stringWithFormat:@"gui-launch-fixed-%.0f.log", [NSDate date].timeIntervalSince1970];
    NSString *logPath = [base stringByAppendingPathComponent:logName];
    [[NSFileManager defaultManager] createFileAtPath:logPath contents:nil attributes:nil];
    NSFileHandle *log = [NSFileHandle fileHandleForWritingAtPath:logPath];
    self.task.standardOutput = log;
    self.task.standardError = log;
    __weak RA2Launcher *weakSelf = self;
    self.task.terminationHandler = ^(NSTask *finished) {
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.stopping) return;
            weakSelf.status.stringValue = finished.terminationStatus == 0 ? @"启动流程已完成，请查看战网窗口。" : @"启动未完成，请查看运行日志。";
        });
    };
    NSError *error = nil;
    if (![self.task launchAndReturnError:&error]) self.status.stringValue = error.localizedDescription;
    else self.status.stringValue = installed ? @"正在启动红警战网…" : @"正在启动战网安装程序，请稍候…";
}
- (void)stopGame:(id)sender {
    self.stopping = YES;
    self.status.stringValue = @"正在结束战网和游戏…";
    self.stopTask = [[NSTask alloc] init];
    self.stopTask.executableURL = [NSURL fileURLWithPath:[self.base stringByAppendingPathComponent:@"runtime/Wine Stable.app/Contents/Resources/wine/bin/wineserver"]];
    self.stopTask.arguments = @[@"-k"];
    NSMutableDictionary *env = [[[NSProcessInfo processInfo] environment] mutableCopy];
    env[@"WINEPREFIX"] = [self.base stringByAppendingPathComponent:@"prefix"];
    [env removeObjectForKey:@"DYLD_INSERT_LIBRARIES"];
    self.stopTask.environment = env;
    __weak RA2Launcher *weakSelf = self;
    self.stopTask.terminationHandler = ^(NSTask *finished) {
        dispatch_async(dispatch_get_main_queue(), ^{
            weakSelf.status.stringValue = finished.terminationStatus == 0 ? @"战网和游戏已结束。" : @"未能结束，请联系我处理。";
        });
    };
    NSError *error = nil;
    if (![self.stopTask launchAndReturnError:&error]) self.status.stringValue = error.localizedDescription;
}
- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender { return YES; }
@end

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        NSApplication *app = [NSApplication sharedApplication];
        RA2Launcher *delegate = [[RA2Launcher alloc] init];
        app.delegate = delegate;
        [app run];
    }
    return 0;
}
