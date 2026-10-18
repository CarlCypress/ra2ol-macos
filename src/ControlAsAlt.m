#import <Cocoa/Cocoa.h>
#import <objc/runtime.h>
#import <IOKit/hidsystem/IOLLEvent.h>
#include <stdio.h>

// Translate before Wine applies its Command -> Windows Ctrl setting.
// Only events delivered to Wine windows are wrapped; no system event tap.
static NSEventModifierFlags controlAsOption(NSEventModifierFlags flags) {
    BOOL left = (flags & NX_DEVICELCTLKEYMASK) != 0;
    BOOL right = (flags & NX_DEVICERCTLKEYMASK) != 0;
    if (!(flags & NSEventModifierFlagControl)) return flags;
    if (!left && !right) left = YES;
    flags &= ~(NSEventModifierFlagControl | NX_DEVICELCTLKEYMASK | NX_DEVICERCTLKEYMASK);
    flags |= NSEventModifierFlagOption;
    if (left) flags |= NX_DEVICELALTKEYMASK;
    if (right) flags |= NX_DEVICERALTKEYMASK;
    return flags;
}

@interface RA2KeyEvent : NSProxy {
    NSEvent *_event;
}
+ (id)wrapping:(NSEvent *)event;
@end
@implementation RA2KeyEvent
+ (id)wrapping:(NSEvent *)event {
    RA2KeyEvent *proxy = [RA2KeyEvent alloc];
    proxy->_event = event;
    return proxy;
}
- (NSEventModifierFlags)modifierFlags { return controlAsOption(_event.modifierFlags); }
- (NSMethodSignature *)methodSignatureForSelector:(SEL)selector {
    return [_event methodSignatureForSelector:selector];
}
- (void)forwardInvocation:(NSInvocation *)invocation { [invocation invokeWithTarget:_event]; }
@end

static NSEvent *mappedEvent(NSEvent *event) {
    if (!event || !(event.modifierFlags & NSEventModifierFlagControl)) return event;
    return (NSEvent *)[RA2KeyEvent wrapping:event];
}

static IMP originalFlagsChanged;
static IMP originalPostKeyEvent;
static void flagsChanged(id window, SEL selector, NSEvent *event) {
    ((void (*)(id, SEL, id))originalFlagsChanged)(window, selector, mappedEvent(event));
}
static void postKeyEvent(id window, SEL selector, NSEvent *event) {
    ((void (*)(id, SEL, id))originalPostKeyEvent)(window, selector, mappedEvent(event));
}

static void installMapping(void) {
    if (originalFlagsChanged) return;
    Class window = objc_getClass("WineWindow");
    if (!window) return;
    Method flags = class_getInstanceMethod(window, @selector(flagsChanged:));
    Method key = class_getInstanceMethod(window, NSSelectorFromString(@"postKeyEvent:"));
    if (!flags || !key) return;
    originalFlagsChanged = method_setImplementation(flags, (IMP)flagsChanged);
    originalPostKeyEvent = method_setImplementation(key, (IMP)postKeyEvent);
    fprintf(stderr, "[RA2 keyboard] Command -> Ctrl; physical Control -> Alt enabled.\n");
}

__attribute__((constructor)) static void initializeMapping(void) {
    @autoreleasepool {
        // winemac is loaded after the Wine loader, so defer until the app runs.
        dispatch_async(dispatch_get_main_queue(), ^{ installMapping(); });
        [[NSNotificationCenter defaultCenter]
            addObserverForName:NSApplicationDidFinishLaunchingNotification object:nil
            queue:nil usingBlock:^(NSNotification *note) { installMapping(); }];
    }
}
