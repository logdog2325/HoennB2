#pragma once
#include "types.h"
#define MI_CpuFill8(p, v, n) memset((p), (v), (n))
#define MI_CpuCopy8(s, d, n) memcpy((d), (s), (n))
