#import <Cocoa/Cocoa.h>
#import <IOKit/hidsystem/IOLLEvent.h>
#include <assert.h>
#include <dlfcn.h>

static NSUInteger received;
@interface WineWindow : NSObject
- (void)flagsChanged:(NSEvent *)event;
- (void)postKeyEvent:(NSEvent *)event;
@end
@implementation WineWindow
- (void)flagsChanged:(NSEvent *)event { received = event.modifierFlags; }
- (void)postKeyEvent:(NSEvent *)event {
    // Wine calls flagsChanged again from postKeyEvent.
    [self flagsChanged:event];
    assert(event.keyCode == 18);
}
@end

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        assert(argc == 2);
        NSString *libraryPath = [NSString stringWithUTF8String:argv[1]];
        void *library = dlopen(libraryPath.fileSystemRepresentation, RTLD_NOW);
        assert(library);
        [[NSNotificationCenter defaultCenter] postNotificationName:NSApplicationDidFinishLaunchingNotification object:nil];
        WineWindow *window = [WineWindow new];
        NSUInteger inputs[] = {
            NSEventModifierFlagControl | NX_DEVICELCTLKEYMASK,
            NSEventModifierFlagControl | NX_DEVICERCTLKEYMASK,
            NSEventModifierFlagCommand | NX_DEVICELCMDKEYMASK,
            NSEventModifierFlagCommand | NX_DEVICERCMDKEYMASK,
            NSEventModifierFlagControl | NX_DEVICELCTLKEYMASK | NSEventModifierFlagCommand | NX_DEVICELCMDKEYMASK,
            NSEventModifierFlagOption | NX_DEVICELALTKEYMASK,
            NSEventModifierFlagShift | NX_DEVICELSHIFTKEYMASK,
            0
        };
        NSUInteger expected[] = {
            NSEventModifierFlagOption | NX_DEVICELALTKEYMASK,
            NSEventModifierFlagOption | NX_DEVICERALTKEYMASK,
            inputs[2], inputs[3],
            NSEventModifierFlagOption | NX_DEVICELALTKEYMASK | NSEventModifierFlagCommand | NX_DEVICELCMDKEYMASK,
            inputs[5], inputs[6], 0
        };
        for (int i = 0; i < 8; ++i) {
            NSEvent *event = [NSEvent keyEventWithType:NSEventTypeKeyDown location:NSZeroPoint
                modifierFlags:inputs[i] timestamp:1 windowNumber:0 context:nil
                characters:@"1" charactersIgnoringModifiers:@"1" isARepeat:NO keyCode:18];
            [window flagsChanged:event];
            assert(received == expected[i]);
            [window postKeyEvent:event];
            assert(received == expected[i]);
        }
        puts("PASS: left/right Control, left/right Command, combined modifiers, Option, Shift, release; direct and nested Wine events.");
    }
    return 0;
}
