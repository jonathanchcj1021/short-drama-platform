# 預設空白 ProGuard 規則（MVP 未開啟混淆）。
# 保留 kotlinx.serialization generated serializer（若未來開啟 R8 再用）。
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.**
-keepclassmembers class **$$serializer { *; }
