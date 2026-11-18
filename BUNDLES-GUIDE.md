# BUNDLES-GUIDE — bundles 工作流 GUID 总结（按图分组）

> 数据口径：bundles 口径索引（608 个带 RegistryContainer 的模式分区，实测全部在 Levels/），
> 与官方 bundles.md 路径同构匹配。★ = 实战用例（VT 模组 AirSuperiority 注入链）。
> 本文件由 tools/gen_bundles_guide.py 从索引数据生成；转储更新后重跑生成器即可刷新。

## 怎么用这些 GUID（官方语义 × 四个场景）

| 场景 | 用哪列 | 语义出处 |
|---|---|---|
| 把内容块带进内存：`ResourceManager:MountSuperBundle('超级包名')`（在 `Level:LoadResources`） | ④ superbundle 名 | custom-content.md：MountSuperBundle 吃**超级包**名（如 `xp3chunks`、`levels/xp3_alborz/xp3_alborz`） |
| 往加载队列里塞 bundle：`Hooks:Install('ResourceManager:LoadBundles', 100, …)` 里改 `bundles` 后 `hook:Pass(bundles, compartment)` | ① bundle 名 | custom-content.md：LoadBundles 队列条目是**bundle**名 |
| 把某图注册内容并入：`AddRegistry(RegistryContainer(Guid(…)))` | ③ RegistryContainer GUID | 案例 04 / venice-ebx-structure §4（AddRegistry 实战） |
| 按实例挂钩：`RegisterInstanceLoadHandler(Guid(分区), Guid(实例), fn)` | ② 分区 GUID + 实例 GUID | custom-content.md / ebx-retrieval.md §2 |
| 运行期定位：`SearchForDataContainer` / `FindInstanceByGuid` | ② 分区 GUID | ebx-retrieval.md §2（只能命中已加载分区） |

> 生命周期与三种注入时机（换图重放 / LoadResources 挂载 / 注册期自消解）见 lua-patterns.md §13。

**两分钟看懂（实战例子就是这条链）**：

```
MountSuperBundle('xp3chunks') + MountSuperBundle('levels/xp3_alborz/xp3_alborz')   ← ④ 超级包
  └─ LoadBundles 注入 'levels/xp3_alborz/rushlarge0'                                ← ① bundle
       └─ 分区 26997AC4-F3C5-42CF-BBC6-CEC65C881911  (Levels/XP3_Alborz/RushLarge0.txt)  ← ②
            └─ RegistryContainer 6C72B9D2-484E-A4D0-94FA-8A8D39357040                  ← ③ AddRegistry 用
```

> 注意：`xp3chunks` 这类 **chunks 超级包不在本表**——它们没有同名分区，角色是"内容块容器"
>（武器/配件数据住里面，靠图包链间接拉起）。

## 附注：compartment——注入的内容进哪个抽屉

注入/注册的内容不是进一个大池子，而是进**带标签的资源隔间**（`ResourceCompartment` 枚举）。
抽屉决定三件事：这些数据**何时加载、何时清空、服务器与客户端各自是否可见**。

| 抽屉 | 值 | 装什么（官方原文意译） |
|---|---|---|
| `Static` | 0 | 启动期加载、关游戏才清的核心数据（共享配置、关卡列表） |
| `Frontend` | 1 | UI 数据与资产（菜单流程） |
| `LoadingScreen` | 2 | 读图画面数据 |
| `Game` | 3 | 某张图的主游戏数据（通常＝主关卡 bundle 全部内容） |
| `Dynamic_Synchronized` | 4–104 | 动态分配——模式包数据（服务器+客户端都加载） |
| `Dynamic_ClientOnly` | 105–205 | 动态分配——武器包数据（仅客户端加载） |

两个实战要点：

1. **`AddRegistry` 官方签名是两个参数**：`(registry, compartment)`，生产模组实战就是**显式两参**
   （VehicleOptics thermal.lua:1174：`AddRegistry(Registry, ResourceCompartment.ResourceCompartment_Game)`）
   ——模式内容一律用 `Game` 抽屉；且 registry 参数需先包成 RegistryContainer：
   `RegistryContainer(ResourceManager:SearchForInstanceByGuid(Guid(RC_GUID)))`。
2. **`LoadBundles` 回调第二参＝队列当前目标隔间**：官方示例原样透传（`hook:Pass(bundles, compartment)`），
   含义是"不改目的地，只改货"——注入的 bundle 跟着队列进它本来的抽屉。

## COOP_002（10 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `AB01_Art_Parent.txt` | `017D39E8-16BD-4422-9EA2-78827A580DC3` | `65FC56CD-E6A9-9051-AAD4-77196EFDEF89` | levels/coop_002/ab01_art_parent | levels/coop_002/coop_002 |
| `AB01_Parent.txt` | `B33B7578-5007-41FB-9F23-CB330F2612F5` | `6750001F-B3C3-DB25-D478-8C2C050DCA37` | levels/coop_002/ab01_parent | levels/coop_002/coop_002 |
| `AB02_Art_Parent.txt` | `30A950B9-8140-4228-B164-F698F9A3EFC1` | `D7968F97-A5AF-706A-6C6C-BBF3EAE56962` | levels/coop_002/ab02_art_parent | levels/coop_002/coop_002 |
| `AB02_Parent.txt` | `42E67C15-DB27-4026-B711-38FDF5E072B8` | `3DFAC248-FB6D-0567-8AB3-521C96D23CD7` | levels/coop_002/ab02_parent | levels/coop_002/coop_002 |
| `AB03_Art_Parent.txt` | `2FB375DD-809D-46C1-914A-C55722CC3A3C` | `49DC7595-49AD-980A-86CE-577E571F99F7` | levels/coop_002/ab03_art_parent | levels/coop_002/coop_002 |
| `AB03_Parent.txt` | `6EFA8841-ECA7-4928-9774-A805F9B72216` | `8AB57FEF-A9FE-CA41-4667-03A429E2E4E1` | levels/coop_002/ab03_parent | levels/coop_002/coop_002 |
| `AB04_Art_Parent.txt` | `823C5278-B4C0-469B-BF0D-2ACB56158373` | `EC41DAB4-0CA2-6834-7AF3-BBF4400439A3` | levels/coop_002/ab04_art_parent | levels/coop_002/coop_002 |
| `COOP_002.txt` | `B1BA4ED2-E692-11DF-8AB9-825AA2E1EF0A` | `C7CE69F5-19C6-D567-CF5F-E5E2CE253A35` | levels/coop_002/coop_002 | levels/coop_002/coop_002 |
| `General_Sluice_AB02_Parent.txt` | `BE8B9F68-6743-4681-BCEC-9F8740A44A20` | `12AFCE46-B655-88C7-741F-461CE7DFF756` | levels/coop_002/general_sluice_ab02_parent | levels/coop_002/coop_002 |
| `General_Sluice_AB03_Parent.txt` | `97677E02-C236-4BEB-8A4D-94AC55CDCC66` | `1D1F5B10-6A8F-28BE-431C-BF14D5252224` | levels/coop_002/general_sluice_ab03_parent | levels/coop_002/coop_002 |

## COOP_003（10 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `AB00_Art_Parent.txt` | `61CAE589-8E22-4911-AF3F-228F0795EDC6` | `A7D1B2DD-882B-37D5-9D31-760A4E29F732` | levels/coop_003/ab00_art_parent | levels/coop_003/coop_003 |
| `AB00_Art_Sewer_Parent.txt` | `B166F91F-9739-4C14-B090-E165CC62E5AE` | `652DEABB-699D-B7B0-8269-D0EC4F2E3ABA` | levels/coop_003/ab00_art_sewer_parent | levels/coop_003/coop_003 |
| `AB00_Parent.txt` | `77428930-7E08-45EB-AC29-5C71D54E8736` | `2E1153C3-C918-665D-C240-8BDD71EC616D` | levels/coop_003/ab00_parent | levels/coop_003/coop_003 |
| `AB00_Sewer_Parent.txt` | `72856E6D-D11E-49DF-9747-C0AD2F34544B` | `1F71ABDC-E0EE-925C-1B0F-4AB2FEB86D12` | levels/coop_003/ab00_sewer_parent | levels/coop_003/coop_003 |
| `AB01_Art_Parent.txt` | `D36D2D3A-050F-4651-B9E5-8AC21EA56938` | `B4CA78C4-C87F-BAD0-F19D-0454A1C6780D` | levels/coop_003/ab01_art_parent | levels/coop_003/coop_003 |
| `AB01_Parent.txt` | `0021F44A-CCA4-4E3F-A15B-22B59A144789` | `B99613C3-4643-B429-BA1A-713EBE4B33D8` | levels/coop_003/ab01_parent | levels/coop_003/coop_003 |
| `AB02_Art_Parent.txt` | `2006CE82-54AD-418A-9C1F-D44B83B654A7` | `5C03BFFC-0F67-4FB0-9EE6-93F4D22C7EC5` | levels/coop_003/ab02_art_parent | levels/coop_003/coop_003 |
| `AB02_Parent.txt` | `8A5F1C77-A680-4E24-9970-2A2B72BADA01` | `AE19BC1A-968D-901B-3274-51C12FEF5058` | levels/coop_003/ab02_parent | levels/coop_003/coop_003 |
| `AB03_Parent.txt` | `CE51D6B0-A60A-4890-84A6-2DF1D9E7E356` | `28D79BA7-E3B3-6A08-A42E-F84AFC36ED5B` | levels/coop_003/ab03_parent | levels/coop_003/coop_003 |
| `COOP_003.txt` | `3D86F044-C978-48CC-8BBB-97474DE4572D` | `81C87B6A-C0B9-33EC-0F96-C101D9F39BC0` | levels/coop_003/coop_003 | levels/coop_003/coop_003 |

## COOP_006（7 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `AB00_Vehicle_MobileAA_Parent.txt` | `40F040E5-163C-4716-A123-41C8ACD5F392` | `61CB4126-2D90-2A39-4B5E-7F4A387DD8F3` | levels/coop_006/ab00_vehicle_mobileaa_parent | levels/coop_006/coop_006 |
| `AB01_GameplayCovers_Parent.txt` | `A1B5A9F2-EDD1-425B-90B2-C6291EFB5DBE` | `48AC0F4A-41BA-4C45-7E2E-85E63DC6BD9B` | levels/coop_006/ab01_gameplaycovers_parent | levels/coop_006/coop_006 |
| `AB01_MortarTeam_Parent.txt` | `EDD69BD1-350B-49D7-9722-78D017FDAD02` | `3056CB59-854C-D91B-1F6E-FA9A7089CBDB` | levels/coop_006/ab01_mortarteam_parent | levels/coop_006/coop_006 |
| `AB01_Parent.txt` | `2EC999A1-999D-44B8-8B7F-50E2C2A12CD0` | `1BAF8336-2290-9590-2EEF-CE057ED61962` | levels/coop_006/ab01_parent | levels/coop_006/coop_006 |
| `AB02_Parent.txt` | `37DA0A1E-6F72-483B-B114-9980624D9BBF` | `4F920518-10C6-185A-FDA6-D305740FA961` | levels/coop_006/ab02_parent | levels/coop_006/coop_006 |
| `AB03_Parent.txt` | `10C54CB7-F90F-4B52-A973-CFCD9B7A9746` | `278C571E-62F1-3B3F-38BB-49117E45401C` | levels/coop_006/ab03_parent | levels/coop_006/coop_006 |
| `COOP_006.txt` | `23535E3D-E72F-11DF-99CA-879440EEBD7A` | `51C54150-0ABF-03BD-EADE-1876AAD3EC8D` | levels/coop_006/coop_006 | levels/coop_006/coop_006 |

## COOP_007（7 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `AB00_Parent.txt` | `7EB13E85-1F8F-4C5F-9683-AFE820226F16` | `0EA13EB4-308E-38A8-8228-2858967BC8DF` | levels/coop_007/ab00_parent | levels/coop_007/coop_007 |
| `AB01_Parent.txt` | `357D693A-304D-4407-A754-98778C6E6D3B` | `7544CD60-941E-EECD-BD81-F022C64E9485` | levels/coop_007/ab01_parent | levels/coop_007/coop_007 |
| `AB02_Parent.txt` | `471BA40B-AF91-46F9-91FB-389C697A2CFA` | `E8BE92C7-91A2-5BA9-0CEE-4AE8642D66A7` | levels/coop_007/ab02_parent | levels/coop_007/coop_007 |
| `AB04_Parent.txt` | `3C1C605A-6804-4756-95F8-AEFF2701E1AD` | `42B5183B-89C8-D6F9-4D84-72386D8A17E0` | levels/coop_007/ab04_parent | levels/coop_007/coop_007 |
| `AB05_Parent.txt` | `B1DF06B9-92F3-4D54-9322-60C60F9F0D1E` | `4CA88055-009C-5110-C25D-810E25A9F71D` | levels/coop_007/ab05_parent | levels/coop_007/coop_007 |
| `COOP_007.txt` | `66606821-E69C-11DF-9B0E-AF9CA6E0236B` | `43DCDEDF-64D3-F3B3-0E66-7C9C71699B20` | levels/coop_007/coop_007 | levels/coop_007/coop_007 |
| `Stadium_Ambience.txt` | `BB37007F-7DF1-4443-99D0-197E93F8F8DB` | `A98CD8E9-2655-E734-2F53-F2F1A9CB31A9` | levels/coop_007/stadium_ambience | levels/coop_007/coop_007 |

## COOP_009（12 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `AB00_Art_Interior_Parent.txt` | `3C48A1DD-F3BC-4480-A948-6DD96AD7357B` | `B2BA2EBF-DB3D-38D5-38B0-BA910B46C0E2` | levels/coop_009/ab00_art_interior_parent | levels/coop_009/coop_009 |
| `AB00_Art_Parent.txt` | `CE9FEA2F-6873-49C7-96AA-23F5C09D8CED` | `FF00FE2E-22C5-5471-FE68-7A85C146AD69` | levels/coop_009/ab00_art_parent | levels/coop_009/coop_009 |
| `AB00_Parent.txt` | `C4D7B947-D5B8-4B77-823A-98A385CE8C44` | `8B3632CD-5291-62F2-35A5-2F2A866C6E7E` | levels/coop_009/ab00_parent | levels/coop_009/coop_009 |
| `AB01_Art_Parent.txt` | `C94188E7-2680-4F23-9199-2DB3403A577C` | `DD6BB416-2481-A007-C6AF-A77F1DD3D0AD` | levels/coop_009/ab01_art_parent | levels/coop_009/coop_009 |
| `AB01_Parent.txt` | `29F2DF1F-DAA4-4B59-9476-BE344414C0A3` | `663AB22D-3413-FD69-37CD-9AF3B068A1A0` | levels/coop_009/ab01_parent | levels/coop_009/coop_009 |
| `AB02_Art_Parent.txt` | `3403ACD0-2601-4520-A492-3148B5BAF291` | `1AFBC64A-E56D-B451-1264-E14A565E441F` | levels/coop_009/ab02_art_parent | levels/coop_009/coop_009 |
| `AB02_Parent.txt` | `3BE12D38-0DC3-4E9D-80C7-B817AD24C9AD` | `EA1453F8-45B1-1D2E-EFB1-1AB5B3A9E71A` | levels/coop_009/ab02_parent | levels/coop_009/coop_009 |
| `AB03_Art_Parent.txt` | `717FAD1D-3BE3-4513-A070-BAB5A2F01B64` | `3D001751-7D38-F603-CCA2-3EF0B7DF849E` | levels/coop_009/ab03_art_parent | levels/coop_009/coop_009 |
| `AB03_Parent.txt` | `8BC56F66-8207-43E9-9926-89759D6D9C4A` | `81FDE91A-18A2-9EA6-873B-4E8FB1855CDE` | levels/coop_009/ab03_parent | levels/coop_009/coop_009 |
| `AB_Art_Road_1_Parent.txt` | `8F6A77D7-B03B-493C-9658-E208EB750A22` | `FCFA0507-8B9A-78CE-C50B-735EA13175B4` | levels/coop_009/ab_art_road_1_parent | levels/coop_009/coop_009 |
| `AB_Art_Road_2_Parent.txt` | `FD65643C-3731-4B80-993D-E9EAA8BFB811` | `89C874F6-2D97-C746-511B-3FAAB72BCD6D` | levels/coop_009/ab_art_road_2_parent | levels/coop_009/coop_009 |
| `COOP_009.txt` | `F94C5091-E69C-11DF-9B0E-AF9CA6E0236B` | `F05798B2-31EC-210D-CC1D-0F7535BECA30` | levels/coop_009/coop_009 | levels/coop_009/coop_009 |

## COOP_010（11 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `AB00_Art_Parent.txt` | `72632A5A-EDBF-41FD-9E05-BC3AA70D7414` | `25BF41F9-0C2B-B2CE-5190-52DF00449EBA` | levels/coop_010/ab00_art_parent | levels/coop_010/coop_010 |
| `AB00_Parent.txt` | `7D853669-609B-4549-A4B8-93329E1B5CB8` | `5FC4F607-8362-F7F1-0353-ACF51A49A611` | levels/coop_010/ab00_parent | levels/coop_010/coop_010 |
| `AB01_AB03_Buffer_Parent.txt` | `3BD4EEB9-CEBC-47AE-984F-3A56CD0E5181` | `E0FA9C4A-D48C-2B6C-33BE-E67A3F03800A` | levels/coop_010/ab01_ab03_buffer_parent | levels/coop_010/coop_010 |
| `AB01_Art_Parent.txt` | `A807F8B9-C218-44E1-A853-6601C10A0541` | `BD65B202-0FA7-F16F-C121-8654FE2F6B30` | levels/coop_010/ab01_art_parent | levels/coop_010/coop_010 |
| `AB01_Parent.txt` | `A296CDBB-3C6D-417B-9DC7-07242F67D356` | `11BFBE88-52FD-1E83-FD62-304C90491FF3` | levels/coop_010/ab01_parent | levels/coop_010/coop_010 |
| `AB03_AB04_Buffer_Parent.txt` | `3ABC2F6E-90CB-49BA-946A-E9617F6BF33C` | `172A09C0-08D3-DFCB-F49C-B147BD6A4BD0` | levels/coop_010/ab03_ab04_buffer_parent | levels/coop_010/coop_010 |
| `AB03_Parent.txt` | `39209766-B25D-4ACE-AAA9-2323A21942A6` | `B1327E0F-83FF-A898-C5D7-25E802EBA799` | levels/coop_010/ab03_parent | levels/coop_010/coop_010 |
| `AB04_Parent.txt` | `93F98810-5CA8-4F65-B048-05821C811A1B` | `1D2D0180-F52B-FD4E-9BBD-AC616EDBD595` | levels/coop_010/ab04_parent | levels/coop_010/coop_010 |
| `AB05_Parent.txt` | `D1D11588-EF17-4DA0-88F2-2CA6E36EEA5D` | `A707A98E-EBE9-E1A8-B75B-162D9ABBC863` | levels/coop_010/ab05_parent | levels/coop_010/coop_010 |
| `AB06_Parent.txt` | `9380DEBB-7BFB-4464-B883-AE230E1932A8` | `DAD8824B-818F-F2D6-F9FB-C624443007D1` | levels/coop_010/ab06_parent | levels/coop_010/coop_010 |
| `COOP_010.txt` | `333BDB92-E69D-11DF-9B0E-AF9CA6E0236B` | `2C804637-3B56-6DDB-92C8-81D094EA806B` | levels/coop_010/coop_010 | levels/coop_010/coop_010 |

## FrontEnd（1 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `FrontEnd.txt` | `E07FE68C-01C4-4262-B215-A3FFDE21234C` | `FED93F47-9267-86B1-3B04-D9405BD49C36` | levels/frontend/frontend | levels/frontend/frontend |

## MP_001（9 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Conquest.txt` | `C98941E6-B300-4D5F-BC2E-ECA03DBF855D` | `59489651-D559-7101-2AA2-41667C1D7FC9` | levels/mp_001/conquest | levels/mp_001/mp_001 |
| `Conquest_Large.txt` | `0CB74E25-485C-4F9F-8CB4-00808FB6F478` | `6AA578EF-F0C1-17CE-16BE-E11B43C3AE23` | levels/mp_001/conquest_large | levels/mp_001/mp_001 |
| `Lightcasters.txt` | `440CF3F0-6F02-46D8-8183-E642A908712C` | `8143E1D5-52B6-69F9-C539-EB5AC9AAE14B` | levels/mp_001/lightcasters | levels/mp_001/mp_001 |
| `MP_001.txt` | `8F5E0383-52A4-11DF-AC80-BC6EA2597601` | `EEBC7D5F-B8BA-A2C8-7C14-CE53212537EE` | levels/mp_001/mp_001 | levels/mp_001/mp_001 |
| `Rush.txt` | `4EE3EABF-AB17-4CEE-9CE5-E02F2C05D9AE` | `3C99FF46-1559-DEE1-7981-D87CCE6F7609` | levels/mp_001/rush | levels/mp_001/mp_001 |
| `Squad_Deathmatch.txt` | `F7A10389-D1BC-4B4A-8E64-F53E4767DEE3` | `18403502-9D98-72CE-13A6-C8C8F52E10E6` | levels/mp_001/squad_deathmatch | levels/mp_001/mp_001 |
| `Squad_Rush.txt` | `646B0E31-52D2-4359-9D6C-3073BE4C2A1A` | `0F472263-879F-0712-12FE-B8F2161ED5EA` | levels/mp_001/squad_rush | levels/mp_001/mp_001 |
| `TDM1.txt` | `631B6F6C-D265-4F62-9134-F291F46DC8F0` | `A071AD6E-FF59-E1AD-246B-B4F15EAD8AD6` | levels/mp_001/tdm1 | levels/mp_001/mp_001 |
| `Team_Deathmatch.txt` | `5D9479AA-B0DB-4783-8CD4-F102FA879EA4` | `A7C44EF2-17C5-EE7A-88CE-1F6ADA25618B` | levels/mp_001/team_deathmatch | levels/mp_001/mp_001 |

## MP_003（10 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Common.txt` | `9505084F-B6D7-4B54-B4C7-5D00CCE12E50` | `A4C75291-186E-35A6-506A-3B42D376C85C` | levels/mp_003/common | levels/mp_003/mp_003 |
| `ConquestLarge.txt` | `188B00C2-5C8E-4438-A6AC-1C0B842ADFC1` | `3E4FA694-FEF9-81FA-07D7-9EA51B8A97E0` | levels/mp_003/conquestlarge | levels/mp_003/mp_003 |
| `ConquestSmall.txt` | `92815F0E-9E3F-4DA4-9CBF-E476E97636CB` | `E6D61955-7C22-01CA-A515-DCB97DF581F8` | levels/mp_003/conquestsmall | levels/mp_003/mp_003 |
| `MP_003.txt` | `62D79D5C-73D9-11DF-920D-853ABDB58E88` | `0B40AC87-7AFF-EDDE-949A-FCBF42CF7126` | levels/mp_003/mp_003 | levels/mp_003/mp_003 |
| `Rush3.txt` | `29BA87E5-2706-40F2-8737-4B8C439B56A8` | `20E11A7B-6440-1FC6-2940-132CDCA6C763` | levels/mp_003/rush3 | levels/mp_003/mp_003 |
| `SquadDeathmatch.txt` | `91F73F4B-0741-49DF-9431-7393B4FAFDD7` | `8C54E8E8-EC1E-D064-8AFF-8EFDA1B51757` | levels/mp_003/squaddeathmatch | levels/mp_003/mp_003 |
| `SquadRush.txt` | `56767ACA-208B-4D0E-89B8-43A2287C0850` | `E1E3C7A1-C0F2-EDC3-7D07-A142590EF2C8` | levels/mp_003/squadrush | levels/mp_003/mp_003 |
| `TDM1.txt` | `05856F5F-4F2B-459A-BC7E-1CE3F5AF9E72` | `7CF7BB96-01AC-D133-343B-E0B2B184CE66` | levels/mp_003/tdm1 | levels/mp_003/mp_003 |
| `TDM2.txt` | `A25CA2DA-54C5-4A67-A967-5E4434EBE6F3` | `DB70CCB8-1448-DFD5-F754-0A765E01BE91` | levels/mp_003/tdm2 | levels/mp_003/mp_003 |
| `TeamDeathmatch.txt` | `DB08932D-A429-4BED-99E8-6FF3B13A68F3` | `254F4954-E586-D5FD-95C5-D7AB3BABD189` | levels/mp_003/teamdeathmatch | levels/mp_003/mp_003 |

## MP_007（9 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Conquest_Large.txt` | `A5CB1ACA-1444-407E-9155-8170AE917840` | `2FA1217E-E0A5-BB41-0509-FDD76537BB78` | levels/mp_007/conquest_large | levels/mp_007/mp_007 |
| `Conquest_Small.txt` | `870CC299-2BC4-4EBC-B854-6219F015D88B` | `A6ED8B5F-1B86-2EA6-B366-45793BD32654` | levels/mp_007/conquest_small | levels/mp_007/mp_007 |
| `MP_007.txt` | `CC4B754F-DC2D-11DF-B4FF-DE2D36FBFBF4` | `958A27B8-F6B4-AE8C-4AE8-1FC8E2AB60BF` | levels/mp_007/mp_007 | levels/mp_007/mp_007 |
| `Rush.txt` | `C72F71D5-751E-46CE-A3B8-FD83D23BA056` | `98FDA983-651E-6FDF-D913-553918EDE291` | levels/mp_007/rush | levels/mp_007/mp_007 |
| `Selective_Art.txt` | `4F0A970D-3CC2-4DD5-8DB7-B2AF0C9097A7` | `11F3F200-A007-B1E3-0E9D-9F2CB9FABC93` | levels/mp_007/selective_art | levels/mp_007/mp_007 |
| `SquadDeathmatch.txt` | `4131FB3F-D9EF-4EF9-BD7C-50E2CDA005E8` | `94B32B56-4AD2-9D2A-419A-78FF86B5CAB1` | levels/mp_007/squaddeathmatch | levels/mp_007/mp_007 |
| `SquadRush.txt` | `4496444F-860F-4E92-9A11-77EB8E32EDBE` | `C327E63A-7B86-2119-9990-C80382D93E42` | levels/mp_007/squadrush | levels/mp_007/mp_007 |
| `TDM1.txt` | `ACD64B25-5F02-40C3-AE68-C83ACC8699BE` | `8322EB21-9961-26C9-6D4F-9AA8C915D48F` | levels/mp_007/tdm1 | levels/mp_007/mp_007 |
| `TeamDeathmatch.txt` | `F372480F-7C8D-48B5-9133-3ECFC0F1D8A9` | `64BD4665-8F19-A6CF-CBC5-A0C4E32B4104` | levels/mp_007/teamdeathmatch | levels/mp_007/mp_007 |

## MP_011（9 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `ArtPCExclusive.txt` | `66D03940-87F9-49B7-8FFD-1A7D6664FD25` | `BCAB7C07-72BE-1F3A-DFA8-B085800C7825` | levels/mp_011/artpcexclusive | levels/mp_011/mp_011 |
| `Conquest_Large.txt` | `07440A24-B275-4796-B1A6-5B70B26F328E` | `CDDEF28D-AC45-4E4C-C9F9-5B671593777E` | levels/mp_011/conquest_large | levels/mp_011/mp_011 |
| `Conquest_Small.txt` | `32533C82-F3F9-4067-A68A-0F1366975981` | `072C4693-37FC-76DE-D034-04889EEDF8EA` | levels/mp_011/conquest_small | levels/mp_011/mp_011 |
| `MP_011.txt` | `28C6D036-DC2A-11DF-BF53-8B1F263C3963` | `D62726FF-B0E2-3619-E95F-57CC5F00D58B` | levels/mp_011/mp_011 | levels/mp_011/mp_011 |
| `Rush.txt` | `393DDAE5-D818-4C6F-BC69-F225858AD8D2` | `3302BEE7-4F8B-F9AF-D63D-F62E237E5994` | levels/mp_011/rush | levels/mp_011/mp_011 |
| `SquadDeathmatch.txt` | `12A8504C-7825-4CC5-BD07-101986DAB481` | `14CCD836-A3AD-8B72-4EBF-BA2AD7A6E445` | levels/mp_011/squaddeathmatch | levels/mp_011/mp_011 |
| `SquadRush.txt` | `A703B87F-BED4-4F62-9FAA-EC540E9B4B8F` | `5B7EF2BA-AF98-4AD1-1055-AF58F0C488C4` | levels/mp_011/squadrush | levels/mp_011/mp_011 |
| `TeamDeathmatch.txt` | `6E53A4AA-A07F-454D-B07B-E9265E0A164D` | `D1081619-49FF-27E0-1C0C-3ACF577D1D00` | levels/mp_011/teamdeathmatch | levels/mp_011/mp_011 |
| `TeamDeathmatch_01.txt` | `15ECEAFB-8ED0-4CB2-B150-EB0DFBFB86D7` | `F6C0DA13-55D3-9BAC-E2DA-AD11FD6CA871` | levels/mp_011/teamdeathmatch_01 | levels/mp_011/mp_011 |

## MP_012（10 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Conquest_Large.txt` | `8DB9CB2A-2A16-44B8-927D-024F1AD06FCF` | `320240BC-173A-5E32-CA75-51E15AC01313` | levels/mp_012/conquest_large | levels/mp_012/mp_012 |
| `Conquest_Small.txt` | `C76217D7-E5B6-459D-9258-2995AFE8ABFB` | `FD6CCF74-3A00-7240-47C6-A93CA989E717` | levels/mp_012/conquest_small | levels/mp_012/mp_012 |
| `MP_012.txt` | `8BB2506F-493A-11DF-B052-CC4B5D6E8131` | `84238275-9EEE-D74E-7D3B-6FDD6A46594A` | levels/mp_012/mp_012 | levels/mp_012/mp_012 |
| `Rush.txt` | `35036BDD-4EC7-471B-8023-256E63566F06` | `5BFAD142-74E4-5332-74EA-831045F98E63` | levels/mp_012/rush | levels/mp_012/mp_012 |
| `SquadDeathmatch.txt` | `025B42C6-12A3-4BFA-9EBA-3C2676301A0E` | `282E15F2-424F-ACE5-BF82-994AAD8AC3D6` | levels/mp_012/squaddeathmatch | levels/mp_012/mp_012 |
| `SquadRush.txt` | `B6A32EF0-896E-4224-9294-BF796E36890A` | `7A4DD5EE-2F11-9C26-A74C-94F66D60D5EF` | levels/mp_012/squadrush | levels/mp_012/mp_012 |
| `TeamDeathmatch.txt` | `41D93E47-8EAA-43DE-A40E-E7F282FB6D91` | `6D360F72-9318-2651-C781-0864609165A7` | levels/mp_012/teamdeathmatch | levels/mp_012/mp_012 |
| `TutorialMP.txt` | `926ACB2D-78FA-4D29-81EC-4E1CDBB9B453` | `A03CBF44-B6AE-DBF8-5993-E40307548F21` | levels/mp_012/tutorialmp | levels/mp_012/mp_012 |
| `TutorialMP_Sandbox.txt` | `254A21D6-82CA-493A-B8EF-D17203B32506` | `00A549F8-7A8A-D253-3099-68D46B31DF0A` | levels/mp_012/tutorialmp_sandbox | levels/mp_012/mp_012 |
| `TutorialMP_ShootHouse.txt` | `869903AD-0EBB-42F6-897B-6DF014962A72` | `66AB221B-5733-BCE3-E1BE-3DF54360251D` | levels/mp_012/tutorialmp_shoothouse | levels/mp_012/mp_012 |

## MP_013（9 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `ConquestLarge.txt` | `1CEC6C7E-1629-4631-B326-1A134BC6EF27` | `6196137B-50D6-4607-98AE-900BACF47065` | levels/mp_013/conquestlarge | levels/mp_013/mp_013 |
| `ConquestSmall.txt` | `BFEA3888-4EF3-4E67-93B4-EAC6645E231F` | `3ACB467B-1D53-8F13-087C-3BA11709105B` | levels/mp_013/conquestsmall | levels/mp_013/mp_013 |
| `MP_013.txt` | `8683F4BB-CD57-11DF-A251-CAB801F86363` | `7C37A538-6C37-4BCF-4FF5-31E534B5C053` | levels/mp_013/mp_013 | levels/mp_013/mp_013 |
| `PC_Only.txt` | `9DDE5EA8-611D-4658-BD52-C5081C155939` | `F69B174D-B6EE-8392-DF71-9F90B4DB4E6D` | levels/mp_013/pc_only | levels/mp_013/mp_013 |
| `Rush.txt` | `8B4AB235-3CD5-4B55-BFA1-4A932119000F` | `812054D9-1693-F438-C445-7A83BAC8DDFE` | levels/mp_013/rush | levels/mp_013/mp_013 |
| `SquadDeathmatch.txt` | `1CE78241-7A1C-452B-A037-3C318DF9130A` | `CE9105DB-E343-C6ED-0492-24045C8739D4` | levels/mp_013/squaddeathmatch | levels/mp_013/mp_013 |
| `SquadRush.txt` | `CFF2E560-DB36-4DD4-B650-0382F7775389` | `518F426E-5459-904F-807B-D62239133910` | levels/mp_013/squadrush | levels/mp_013/mp_013 |
| `TDM1.txt` | `A53E6FD6-C658-4DCE-9A66-4CC1CC895349` | `F1C35971-5D33-EF6A-DE15-1C3C7D2C027A` | levels/mp_013/tdm1 | levels/mp_013/mp_013 |
| `TeamDeathmatch.txt` | `B24034BE-6980-4EA7-AAC3-65261891C0B0` | `57E090A3-CE3A-0574-9946-67EE29684AED` | levels/mp_013/teamdeathmatch | levels/mp_013/mp_013 |

## MP_017（7 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `CQL.txt` | `74CB44C4-DD2E-4CB2-9914-C2579E68567B` | `2F574B5B-D74B-62E8-43BF-18D8EB32939E` | levels/mp_017/cql | levels/mp_017/mp_017 |
| `CQS.txt` | `2D2BDA9A-A4B7-4012-9340-7F8CA94B2D97` | `CD39A611-8445-E2CE-6F6D-1BB085864E0C` | levels/mp_017/cqs | levels/mp_017/mp_017 |
| `MP_017.txt` | `D1A27F63-3380-11E0-9C69-F35878AF207B` | `D8CCDDDF-03EF-8341-95AB-B6458DEEE07D` | levels/mp_017/mp_017 | levels/mp_017/mp_017 |
| `R.txt` | `D9E8DC6C-250E-4AF9-9878-07809B5AE5D9` | `33FF3424-F0C5-9A3A-5C0F-A49573416A13` | levels/mp_017/r | levels/mp_017/mp_017 |
| `SDM.txt` | `8C3A1DE3-E97C-4CFE-9C52-AD15228B256B` | `E50373BD-DD17-8EEF-94A0-9499B81BD4CA` | levels/mp_017/sdm | levels/mp_017/mp_017 |
| `SR.txt` | `F713048D-9E41-4B6C-842C-6BE7F0D7DC51` | `DF50AC17-91A9-7A0C-AB6E-61B2A6E78461` | levels/mp_017/sr | levels/mp_017/mp_017 |
| `TDM.txt` | `BF04112A-BD58-42D4-B5CB-57BB8B6D66DA` | `AECC7763-C8A2-A540-11C9-ED797F7AAF1F` | levels/mp_017/tdm | levels/mp_017/mp_017 |

## MP_018（12 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Conquest.txt` | `AB4A6F8A-E869-42F5-91CC-F11901FDBAB1` | `5E1C198C-E64F-5098-CE88-EB51E1557E23` | levels/mp_018/conquest | levels/mp_018/mp_018 |
| `Conquest_Large.txt` | `6CC0E060-AF87-4A74-9CD2-475B06D8A972` | `A50A9688-4DA3-6B2E-D9B4-C9006EF2544B` | levels/mp_018/conquest_large | levels/mp_018/mp_018 |
| `Conquest_Large2.txt` | `17BEE2E7-8159-48C9-BB90-9225FD3225DB` | `5CA6F293-6945-DE04-6DF5-EE026B1DB26C` | levels/mp_018/conquest_large2 | levels/mp_018/mp_018 |
| `Conquest_Small.txt` | `AD88A8A6-43E7-464B-918A-54B817A09E6B` | `94A8DEF8-AE7A-CA3E-F77B-880F6298726F` | levels/mp_018/conquest_small | levels/mp_018/mp_018 |
| `Conquest_Small2.txt` | `65AAA734-6CE2-4CDA-AABC-2F2E63676162` | `B28DEDF0-7CE5-4BB3-9D95-62F0BC52E65F` | levels/mp_018/conquest_small2 | levels/mp_018/mp_018 |
| `MP_018.txt` | `509DD08F-CA40-11DF-959F-F75C97057931` | `2DA72E11-1162-F2FE-47A3-CEE3DD5CF72D` | levels/mp_018/mp_018 | levels/mp_018/mp_018 |
| `MP_Global2.txt` | `172285B7-3AC9-46DC-BB3D-5DE7AC0D1C91` | `39B4C327-705B-EC19-5BCB-12A0733E58AB` | levels/mp_018/mp_global2 | levels/mp_018/mp_018 |
| `Rush.txt` | `D05322FF-9AC2-45AE-B654-FCAA4C4B4F8F` | `4AE27648-E2C7-C3D6-0E25-5E3D05227153` | levels/mp_018/rush | levels/mp_018/mp_018 |
| `SquadDeathmatch.txt` | `390CB8AE-4A09-48D4-B8CD-A36DA86E2AA9` | `BCAE2870-2B50-22CF-A8EB-76E71E062479` | levels/mp_018/squaddeathmatch | levels/mp_018/mp_018 |
| `SquadRush.txt` | `025C3522-FEC5-4910-9189-56116A85998D` | `274BBDAE-66F7-7934-E3B6-C7C9EF6965B6` | levels/mp_018/squadrush | levels/mp_018/mp_018 |
| `TDM1.txt` | `98EF290B-9626-47D1-B81F-F4F7D8A1DC0A` | `C92F7CB9-EB9C-908E-5237-553696A1C855` | levels/mp_018/tdm1 | levels/mp_018/mp_018 |
| `TeamDeathmatch.txt` | `33EBD9D3-5F5B-4668-B2D2-330B97753C90` | `F0FE1DA4-9172-AC1E-4793-9F9F857E6EA7` | levels/mp_018/teamdeathmatch | levels/mp_018/mp_018 |

## MP_Subway（12 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Common.txt` | `7DEBF99E-FD4C-4658-A377-BF75948E0605` | `4E9880DB-2D54-58B3-6A31-F7B26567D785` | levels/mp_subway/common | levels/mp_subway/mp_subway |
| `Conquest_Small.txt` | `0964415F-1A6E-4BA3-A11D-EEDDF2DB9FD2` | `711883E6-D355-9753-9C3B-A933FA58F329` | levels/mp_subway/conquest_small | levels/mp_subway/mp_subway |
| `GamePlayObjects.txt` | `067CA90C-107A-43EB-A7D3-82754A5948CD` | `FE0188C4-2849-6183-AA4E-878EA40DE6AB` | levels/mp_subway/gameplayobjects | levels/mp_subway/mp_subway |
| `MP_Subway.txt` | `88D61A88-ECC8-11DF-B39C-FD673456481D` | `F98F36A2-3A59-A7E0-ABC5-240CB4C88307` | levels/mp_subway/mp_subway | levels/mp_subway/mp_subway |
| `Rush.txt` | `5327EB00-5EE0-4027-90E2-24381211C72E` | `3337A0DC-12FA-F5FF-7547-FCB28E23ADA4` | levels/mp_subway/rush | levels/mp_subway/mp_subway |
| `SquadDeathmatch.txt` | `EBA44787-EECF-49BA-937A-7BB63190641D` | `91C3778A-8396-EC58-F1D2-16C4C10B3238` | levels/mp_subway/squaddeathmatch | levels/mp_subway/mp_subway |
| `SquadRush.txt` | `73A06F9C-11C7-404E-9CEF-24F0558BAD5F` | `1AB92146-CFB6-6C88-C6CE-99CFD048DC59` | levels/mp_subway/squadrush | levels/mp_subway/mp_subway |
| `TDM1.txt` | `9507992B-64C8-45B8-B327-11EFEE44AC56` | `F569E379-21E8-0073-7465-2B38563639C9` | levels/mp_subway/tdm1 | levels/mp_subway/mp_subway |
| `TDM2.txt` | `DC440171-3D3B-491B-8D27-D2BD3C6AAF30` | `B466629B-20BA-F30B-7ABF-0F7F4E07B222` | levels/mp_subway/tdm2 | levels/mp_subway/mp_subway |
| `TeamDeathmatch.txt` | `407BD66A-8897-4FEC-9A9A-8959507805FE` | `F4ED40BF-9370-FE10-7735-15B7D6126D5F` | levels/mp_subway/teamdeathmatch | levels/mp_subway/mp_subway |
| `Teams_Large.txt` | `7E037C78-ACE0-43A0-AD6C-168490C464C7` | `13103A15-2A58-56A4-4D62-8FE23D4FC466` | levels/mp_subway/teams_large | levels/mp_subway/mp_subway |
| `Teams_Small.txt` | `99A2428B-0611-4941-869D-C0AAB0D97CAE` | `9836C728-6C32-8E3B-D410-48BDA432E02E` | levels/mp_subway/teams_small | levels/mp_subway/mp_subway |

## SP_Bank（47 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `AssaultCanalProps_SUB.txt` | `21B110D8-F043-4344-9A5B-1F48FB9F2A18` | `0B118B30-5470-C195-F961-D3B442830F12` | levels/sp_bank/assaultcanalprops_sub | levels/sp_bank/sp_bank |
| `Assault_SUB.txt` | `DA3CE5E8-F14A-41EA-86E6-4CCC155087BF` | `9F597E4C-E999-2AEC-B013-420BF8F311B4` | levels/sp_bank/assault_sub | levels/sp_bank/sp_bank |
| `BMD.txt` | `A0229B33-9D6D-49C5-92F3-163BC9823969` | `7B85FE02-0D9C-347A-E1FF-8A1BF667BCA6` | levels/sp_bank/bmd | levels/sp_bank/sp_bank |
| `Backdrop.txt` | `CD38C7AE-78F6-4ADD-BCE0-F86D0BF497A1` | `9B7EA234-F13F-CDFA-1CC8-64B894342740` | levels/sp_bank/backdrop | levels/sp_bank/sp_bank |
| `BackdropHighway_SUB.txt` | `EDE89B74-86C8-4712-906F-C4BA4DEE41F8` | `7FA4C014-CDA5-FDCF-DFA0-14DDE63F6618` | levels/sp_bank/backdrophighway_sub | levels/sp_bank/sp_bank |
| `Bank_SUB.txt` | `78EE7B6D-3A68-45B6-8D21-C002D9233B5C` | `CD4A4DF4-C396-DDA3-A287-3E5B5F77C29A` | levels/sp_bank/bank_sub | levels/sp_bank/sp_bank |
| `Breach_SUB.txt` | `E6789E75-5CC4-4D35-9254-B47D915B9886` | `46BCD2FB-90BC-D05D-EDEE-99CFDFC3311C` | levels/sp_bank/breach_sub | levels/sp_bank/sp_bank |
| `Bridge_SUB.txt` | `A8F79535-D168-4DE6-AEA1-C81DEFA3B8BF` | `96EB456B-99D6-264E-BCD7-A7725E9A4C5F` | levels/sp_bank/bridge_sub | levels/sp_bank/sp_bank |
| `Convoy_Art_SUB.txt` | `B547DB42-DD9F-4811-BA65-BA956E544F08` | `6C7B0969-7B51-A423-8ED8-4F200A74BEDA` | levels/sp_bank/convoy_art_sub | levels/sp_bank/sp_bank |
| `Convoy_SUB.txt` | `9BE77410-ADCD-4527-B673-F3B23C22D0E2` | `BBFD1453-6F5A-323B-C2C4-B05981DD681E` | levels/sp_bank/convoy_sub | levels/sp_bank/sp_bank |
| `Convoy_Start_SUB.txt` | `3AA69DFB-EE53-4BA8-9872-D4B04F34D377` | `6A871848-8D3F-BB4D-3076-E83C4A9566CC` | levels/sp_bank/convoy_start_sub | levels/sp_bank/sp_bank |
| `Highway_01_Ambience_SUB.txt` | `181D82AD-1D84-4DB7-BD8D-CDA5EE172AB1` | `86265AC6-ECCB-05A7-0838-F2D220AAB5D7` | levels/sp_bank/highway_01_ambience_sub | levels/sp_bank/sp_bank |
| `Highway_01_SUB.txt` | `121135DD-196E-4B76-B13F-CE9DB70F2031` | `D7E6CDFC-592D-CA13-BE4C-FF0F84A502EF` | levels/sp_bank/highway_01_sub | levels/sp_bank/sp_bank |
| `Highway_02_SUB.txt` | `1713EBDE-EE33-4793-BDFB-5FFD57D9EE7F` | `5E0D28C5-937D-D02C-AF99-ED7D4F5E2905` | levels/sp_bank/highway_02_sub | levels/sp_bank/sp_bank |
| `Highway_03_Ambience_SUB.txt` | `EA7238F4-F530-4ECE-BA52-433D08F7DA3E` | `8010E9F6-6309-FAF3-3CB9-0B0B47DBCDC3` | levels/sp_bank/highway_03_ambience_sub | levels/sp_bank/sp_bank |
| `Highway_03_Props.txt` | `ADBC0BCC-7CBE-4ED7-88B3-EACF0BE20384` | `DFD92AF1-2F7C-C9D2-57DB-85B81F19EB3B` | levels/sp_bank/highway_03_props | levels/sp_bank/sp_bank |
| `Highway_03_SUB.txt` | `1652E3D8-6BC2-4216-B294-10A7EB26DB56` | `46350ED2-D88A-4A34-ECDB-0BB8207BBC69` | levels/sp_bank/highway_03_sub | levels/sp_bank/sp_bank |
| `House_ART_SUB.txt` | `5BCA256F-DBEF-44C9-9B33-7B3AEF2705C2` | `87F0D991-DE89-392A-2B70-E69F5621CA5C` | levels/sp_bank/house_art_sub | levels/sp_bank/sp_bank |
| `House_Props_SUB.txt` | `3ABF45B4-626A-46F7-A709-CFA1AED1BCB4` | `C6F48FA7-0C8B-BDE7-20F3-D0616EE9D922` | levels/sp_bank/house_props_sub | levels/sp_bank/sp_bank |
| `House_SUB.txt` | `9DD8DAA5-87BF-458D-9BCB-986392495724` | `831621C0-DC75-6EDA-B098-B4ADA777ADB3` | levels/sp_bank/house_sub | levels/sp_bank/sp_bank |
| `Intro_SUB.txt` | `18360729-D65A-4FBC-B667-AB79B1F36EA9` | `76EC83D6-337F-FF34-B1CF-9B6C9C0D03B0` | levels/sp_bank/intro_sub | levels/sp_bank/sp_bank |
| `LightMap_01.txt` | `51F2C993-93C4-438E-8215-FF0A571A65EB` | `8A65C3F4-2E23-2A1D-3D48-A6E2A85F2EC2` | levels/sp_bank/lightmap_01 | levels/sp_bank/sp_bank |
| `LightMap_02.txt` | `3206282A-B910-47CB-B76E-0C599084ED3D` | `9F10BAC5-B3B8-8ECA-890B-69A140BDC656` | levels/sp_bank/lightmap_02 | levels/sp_bank/sp_bank |
| `LightMap_03.txt` | `FCCD1F7B-310A-419F-90D0-29EA70693335` | `A39348A8-6F0D-5E58-7B30-1A94B4E7CA79` | levels/sp_bank/lightmap_03 | levels/sp_bank/sp_bank |
| `LightMap_04.txt` | `342D5BDA-CC0D-46F9-A271-5A69CD16FBC8` | `F685E9C7-5797-3757-ADC6-208E57C04B76` | levels/sp_bank/lightmap_04 | levels/sp_bank/sp_bank |
| `MARINES.txt` | `2EC2734A-0F06-4D50-BCEC-A26D8DC55EFC` | `B240E1D4-FF0A-E30E-F093-834798FE8820` | levels/sp_bank/marines | levels/sp_bank/sp_bank |
| `MARINES2.txt` | `56221A1D-9F9C-4948-8F98-323403455296` | `2C786490-E871-85C2-F12D-252646E8317C` | levels/sp_bank/marines2 | levels/sp_bank/sp_bank |
| `Ministry_Ambience_SUB.txt` | `381448FE-97B1-4C9D-8160-2526060AF408` | `DC438B6D-A083-AD6E-94AC-763CB7118E06` | levels/sp_bank/ministry_ambience_sub | levels/sp_bank/sp_bank |
| `Ministry_SUB.txt` | `65BC2EEA-F91E-4E58-8AD0-9383153D21C1` | `A2237AE5-4CA5-5C5C-96A2-1597CA6F58E7` | levels/sp_bank/ministry_sub | levels/sp_bank/sp_bank |
| `Passage_CUTSCENE.txt` | `BD2CA089-D2F1-4F87-BCD8-5A8766591663` | `B9B149C1-D44C-D151-67F7-4D05736A5EF5` | levels/sp_bank/passage_cutscene | levels/sp_bank/sp_bank |
| `Passage_SUB.txt` | `5E8D6D43-07BB-4C61-A9BF-EA167BAED78B` | `45B1C9AC-F296-37A6-D0E0-5DCE6EE5A85B` | levels/sp_bank/passage_sub | levels/sp_bank/sp_bank |
| `Plaza.txt` | `D2E7BA48-BD94-47F7-9815-754C841357B1` | `F0E67AA5-E856-2A90-98F6-8C5942CB3F60` | levels/sp_bank/plaza | levels/sp_bank/sp_bank |
| `PlazaLightz_SUB.txt` | `E0DC3FBD-68D1-45BE-A31D-27F26590FE8A` | `E4D6BF63-E48F-3056-4692-4DD140C12AF6` | levels/sp_bank/plazalightz_sub | levels/sp_bank/sp_bank |
| `PlazaProps_SUB.txt` | `F70737E0-CEE7-4EE0-91EF-5705B33C6D8B` | `65B79118-FCD5-EC78-DC00-F3FE63163ED7` | levels/sp_bank/plazaprops_sub | levels/sp_bank/sp_bank |
| `Plaza_Interior_SUB.txt` | `3DBA0ABB-1C24-4F30-92DE-8BCD39AF88F5` | `C59DD26E-99D7-03CF-1E2E-A78B58E2317B` | levels/sp_bank/plaza_interior_sub | levels/sp_bank/sp_bank |
| `REGROUP.txt` | `2F97DFAD-30D7-4253-B488-D6DB45E4FB8E` | `98522C78-DC06-84F6-1DCD-B67756EE3193` | levels/sp_bank/regroup | levels/sp_bank/sp_bank |
| `Ride_Ambience_SUB.txt` | `B4697975-DB23-49F0-AA89-465F3B56BD7F` | `CD48675D-4919-2451-1763-2B200314BF32` | levels/sp_bank/ride_ambience_sub | levels/sp_bank/sp_bank |
| `Ride_SUB.txt` | `8148A1BB-8F21-4E40-8A8F-2126000ABCD4` | `9F9CABAF-21C2-EF4A-B35D-4358AEBA7565` | levels/sp_bank/ride_sub | levels/sp_bank/sp_bank |
| `SP_Bank.txt` | `5119BCE8-E277-11DF-AC57-D4F216B966DB` | `3CE59905-42E2-0A0B-2582-8EE6B7CB6FB5` | levels/sp_bank/sp_bank | levels/sp_bank/sp_bank |
| `Tank_ART_SUB.txt` | `B16BC0CE-ED21-4D6E-8F48-C414F0F3BB8E` | `0BCF64BB-D70E-AFDB-2D63-6C829B333B09` | levels/sp_bank/tank_art_sub | levels/sp_bank/sp_bank |
| `Tank_SUB.txt` | `ACB01A32-1C60-4591-AF99-E12936A139F3` | `8D8CC5E7-EBA1-5D11-D79E-A67BEDF010BC` | levels/sp_bank/tank_sub | levels/sp_bank/sp_bank |
| `TrenchIntro.txt` | `66447827-7B72-4D09-870F-34A93FFD7E0D` | `33619D35-6244-CD66-7593-D506DBBF9F3C` | levels/sp_bank/trenchintro | levels/sp_bank/sp_bank |
| `VaultART_SUB.txt` | `96478831-B8EE-45DA-939B-71B83FFDAEAC` | `55592C91-90A9-8F88-0F46-E9C865CC3953` | levels/sp_bank/vaultart_sub | levels/sp_bank/sp_bank |
| `VaultDescentAnimations.txt` | `DBDA1714-AF78-4120-B213-FD1A3F3ED5BE` | `BDAC892E-F7EE-62AB-B520-947BC1E8C856` | levels/sp_bank/vaultdescentanimations | levels/sp_bank/sp_bank |
| `VaultEndAnimations.txt` | `6BE254CB-C17C-4A2F-BF93-2B4D31F266AF` | `1580708E-8507-42A7-1246-004863638402` | levels/sp_bank/vaultendanimations | levels/sp_bank/sp_bank |
| `VaultStream_SUB.txt` | `5D409A1F-DBF3-42F9-8733-01BDEBD2727A` | `80A89AC6-18D8-2B4A-B8AB-4F14744D24E2` | levels/sp_bank/vaultstream_sub | levels/sp_bank/sp_bank |
| `Vault_SUB.txt` | `7580AF15-F26C-457B-80A4-08D7BE549927` | `E9F1A353-C3DE-9630-E23B-C893F906E05B` | levels/sp_bank/vault_sub | levels/sp_bank/sp_bank |

## SP_Earthquake（29 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Alley.txt` | `11A4ED05-AF2E-46EC-8799-D27A1FBA7FD0` | `5BB0C64A-181C-9151-331E-115CACE29218` | levels/sp_earthquake/alley | levels/sp_earthquake/sp_earthquake |
| `Backdrop.txt` | `6CAE0C9E-DC0B-420D-87A1-00376E74BA46` | `9AE4AF9B-6CF0-7728-614B-68A8E3AE5A19` | levels/sp_earthquake/backdrop | levels/sp_earthquake/sp_earthquake |
| `Bazaar.txt` | `3734F519-F0D7-4F24-A11F-3428126B27B8` | `D27FC0B3-C259-BE32-E3D3-40E0121C416A` | levels/sp_earthquake/bazaar | levels/sp_earthquake/sp_earthquake |
| `BazaarFacade.txt` | `9CB0031D-85D6-4776-A865-06AF450CB5AA` | `7860ED51-4FD0-622C-30CA-E0007EFD3260` | levels/sp_earthquake/bazaarfacade | levels/sp_earthquake/sp_earthquake |
| `BridgeFight.txt` | `E3FC2659-8FE4-40B0-9E45-791C51C19135` | `DD539376-E1FC-10C3-EEFE-98E6317BC60F` | levels/sp_earthquake/bridgefight | levels/sp_earthquake/sp_earthquake |
| `Briefing.txt` | `1E994B3B-D7FE-4D4A-ACF6-AC3E8136766A` | `427937FE-98ED-FAE3-C74F-0040FFD75E98` | levels/sp_earthquake/briefing | levels/sp_earthquake/sp_earthquake |
| `Building.txt` | `1A2A0C9B-25D0-45BF-BF2D-61E9981A1F65` | `6AD744C5-26B5-B864-B37C-272BFE25E426` | levels/sp_earthquake/building | levels/sp_earthquake/sp_earthquake |
| `Cellar.txt` | `892B57BC-026C-4882-96F6-CD23AB171CE4` | `C86D2732-8303-8808-7A31-09511633DA74` | levels/sp_earthquake/cellar | levels/sp_earthquake/sp_earthquake |
| `Earthquake.txt` | `E5E15C7F-BE8D-4CD5-B00B-EC50500D88C4` | `13EC7EF9-8C1B-95E2-02FD-6697211EE768` | levels/sp_earthquake/earthquake | levels/sp_earthquake/sp_earthquake |
| `IED.txt` | `137B2CA6-608C-4D25-8D00-1682B3F257E1` | `C4E21952-6308-7659-C351-0179D2AA4D58` | levels/sp_earthquake/ied | levels/sp_earthquake/sp_earthquake |
| `LAVScene.txt` | `D716CAB3-FF50-4184-A139-067C48F2E0E4` | `2BE2259A-809E-8849-F7FE-9074DD897CBD` | levels/sp_earthquake/lavscene | levels/sp_earthquake/sp_earthquake |
| `LAVSceneOccluders.txt` | `537F4D38-586B-4E7E-8D34-7BA4D4B7C2BF` | `43AE0C20-BB6C-84FF-500C-9E1D02B432E3` | levels/sp_earthquake/lavsceneoccluders | levels/sp_earthquake/sp_earthquake |
| `LightMap_01.txt` | `5AE86B84-964D-409E-B830-B6A0E8B4EDB2` | `22668000-6487-F3A9-DF7B-3E5DF676F3B6` | levels/sp_earthquake/lightmap_01 | levels/sp_earthquake/sp_earthquake |
| `LightMap_02.txt` | `2A24C9DB-534A-42EE-B40F-F35E25470A68` | `B1A08CB2-7E24-8AD1-D089-B51E1C98BC73` | levels/sp_earthquake/lightmap_02 | levels/sp_earthquake/sp_earthquake |
| `LightMap_03.txt` | `FDF9893D-A7ED-4513-B1E7-5C0A3976C128` | `DF079E1D-3F3D-CB06-F11B-F9ECD0D26722` | levels/sp_earthquake/lightmap_03 | levels/sp_earthquake/sp_earthquake |
| `MeatMarket.txt` | `126DD4FE-FA0F-4AC0-A77C-5D7C0FE8A27F` | `662DB884-4563-032E-577B-618322AD0F70` | levels/sp_earthquake/meatmarket | levels/sp_earthquake/sp_earthquake |
| `ParkingLot.txt` | `AE93EB52-EA1A-434A-BFC3-22FD49312572` | `08FF5E94-1FFD-88DC-6F9C-4A158B062252` | levels/sp_earthquake/parkinglot | levels/sp_earthquake/sp_earthquake |
| `ParkingLotSurroundings.txt` | `669F28A5-B195-4067-B070-E96D87CF1D32` | `E887D84B-05A0-22C6-A3D0-4F5AB5E1A6A1` | levels/sp_earthquake/parkinglotsurroundings | levels/sp_earthquake/sp_earthquake |
| `Rooftop.txt` | `D4D89981-F298-43AE-93E3-42B008B2DB44` | `CCD3CB90-2F47-D1C6-7C3C-52D64A58C525` | levels/sp_earthquake/rooftop | levels/sp_earthquake/sp_earthquake |
| `RooftopExtraction.txt` | `44D790D6-AEB5-4926-AD03-DAB35BEE9510` | `DB59BD6C-1464-46C4-13A3-87E1B34E23F6` | levels/sp_earthquake/rooftopextraction | levels/sp_earthquake/sp_earthquake |
| `RooftopParkour.txt` | `B20FE0AB-13D3-4129-B3B4-4FE78AAF430F` | `81BD0E67-3274-2361-A195-63C83986C2B8` | levels/sp_earthquake/rooftopparkour | levels/sp_earthquake/sp_earthquake |
| `RooftopSniper.txt` | `5D950055-C75C-4021-B64E-BCFB213BB312` | `BFD89C8A-7878-5B84-06F9-F2630514790C` | levels/sp_earthquake/rooftopsniper | levels/sp_earthquake/sp_earthquake |
| `SP_Earthquake.txt` | `C8D40579-CA37-11DF-B1FE-C90CED16BE7F` | `11708A3E-B3DD-AB17-990A-AAA36E649ACB` | levels/sp_earthquake/sp_earthquake | levels/sp_earthquake/sp_earthquake |
| `School.txt` | `7D7D8758-DA42-42D8-AF74-D441021FE9D6` | `66B3304A-6ACE-87EB-234E-054E17101488` | levels/sp_earthquake/school | levels/sp_earthquake/sp_earthquake |
| `SchoolBuilding.txt` | `3ADD7261-E9D1-46A6-9695-94435082A8C9` | `0809412E-74CC-BDDD-304A-84682BDD7C42` | levels/sp_earthquake/schoolbuilding | levels/sp_earthquake/sp_earthquake |
| `StagingArea.txt` | `6FD29080-4955-4D72-8FF7-3A5930061079` | `9A0446B5-5F21-A760-5126-AB1596C82E2C` | levels/sp_earthquake/stagingarea | levels/sp_earthquake/sp_earthquake |
| `StagingAreaSurroundings.txt` | `82112183-EF56-4550-8673-3D11825DC4A7` | `64BE2EE7-2C2E-E02B-1A15-47E24D0928B7` | levels/sp_earthquake/stagingareasurroundings | levels/sp_earthquake/sp_earthquake |
| `StagingAreaWin32.txt` | `85FEB6B6-766F-44BC-844F-517234731865` | `FADD6FCD-CEF3-E301-AA88-F5A1F826551A` | levels/sp_earthquake/stagingareawin32 | levels/sp_earthquake/sp_earthquake |
| `StreetCrossing.txt` | `853C4BF7-1023-4338-87DB-3EDA73FE36B6` | `A7859305-3BA6-79CA-3147-04B704547C88` | levels/sp_earthquake/streetcrossing | levels/sp_earthquake/sp_earthquake |

## SP_Earthquake2（19 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Alley_SUB.txt` | `AC8F22DC-08C0-46AF-8E42-42F5CA900991` | `DD3E34B8-4258-1493-7A33-C60B2F2C2C2F` | levels/sp_earthquake2/alley_sub | levels/sp_earthquake2/sp_earthquake2 |
| `Backdrop.txt` | `3E2A47E7-B74B-42AE-909F-6E16EDC995A7` | `B6897A94-9934-FE16-0479-54B1A65ADAE5` | levels/sp_earthquake2/backdrop | levels/sp_earthquake2/sp_earthquake2 |
| `Bazaar_SUB.txt` | `37FC0AB0-D0A7-4899-A5EA-B2C61E566B9D` | `2F746428-9ABB-5786-8B0B-336F4C2B24CC` | levels/sp_earthquake2/bazaar_sub | levels/sp_earthquake2/sp_earthquake2 |
| `Cafe_DOORSUB.txt` | `2EB721A0-8CC9-4711-A47A-47DE14460486` | `64201C59-44B4-4A9F-6CE5-973767839A14` | levels/sp_earthquake2/cafe_doorsub | levels/sp_earthquake2/sp_earthquake2 |
| `Cafe_MEETMONTES.txt` | `C98E9D6E-7CC0-41AC-BB3E-048730ADD267` | `E1AB7D8A-3658-65BD-D7DC-8738BBF5C344` | levels/sp_earthquake2/cafe_meetmontes | levels/sp_earthquake2/sp_earthquake2 |
| `Cafe_SUB.txt` | `97C8B6A2-B913-47EF-8B7E-2FAA0230D27E` | `0F5C7DE3-2B77-EAB1-90CC-14F7399B82DA` | levels/sp_earthquake2/cafe_sub | levels/sp_earthquake2/sp_earthquake2 |
| `LargeBuilding_SUB.txt` | `CB86E58F-ADD1-4E20-B47B-B34005A07733` | `F8BA1C04-59B7-EE2E-48FC-7A91F73AB53E` | levels/sp_earthquake2/largebuilding_sub | levels/sp_earthquake2/sp_earthquake2 |
| `LightMap_01.txt` | `C61EACEB-457E-41B8-B329-4F222500EF26` | `90905877-72C1-5FAF-D349-50204FE6B65F` | levels/sp_earthquake2/lightmap_01 | levels/sp_earthquake2/sp_earthquake2 |
| `LightMap_02.txt` | `4472F1A7-11B8-4F1C-B4D5-2FB7447863E5` | `1929510E-92A3-9B9B-0A26-80D66E21562C` | levels/sp_earthquake2/lightmap_02 | levels/sp_earthquake2/sp_earthquake2 |
| `LightMap_03.txt` | `33E1C9DB-AC62-4B11-B13F-3870410E8C82` | `EE2BE878-E185-1522-DF1D-B5D49BE564DD` | levels/sp_earthquake2/lightmap_03 | levels/sp_earthquake2/sp_earthquake2 |
| `MeatMarket_SUB.txt` | `71C9B35F-8F33-4789-8D2D-0F42A99ABA17` | `A6F8C8FC-E43E-FF3A-8FF7-5571B184B180` | levels/sp_earthquake2/meatmarket_sub | levels/sp_earthquake2/sp_earthquake2 |
| `ParkingLot_SUB.txt` | `79C69C11-9C46-441E-92A3-48CAA1F9A529` | `4C0CA763-8EF1-89EA-0501-87665036008B` | levels/sp_earthquake2/parkinglot_sub | levels/sp_earthquake2/sp_earthquake2 |
| `Rift2_SUB.txt` | `F39F328C-6A29-49F4-9198-832D559186D1` | `5C70EABD-F9B6-E550-60CA-189B1EF2628B` | levels/sp_earthquake2/rift2_sub | levels/sp_earthquake2/sp_earthquake2 |
| `Rift_SUB.txt` | `FB9BE436-CF98-40D9-B1F9-85D462E30FCB` | `46FD1469-F79C-2EDE-A423-0FCF94F4A39A` | levels/sp_earthquake2/rift_sub | levels/sp_earthquake2/sp_earthquake2 |
| `SP_Earthquake2.txt` | `6FD69AE4-5B8A-11E0-BC14-D5B461CF665B` | `7C9240B4-8C13-9DCA-B21F-E436E9A79F8F` | levels/sp_earthquake2/sp_earthquake2 | levels/sp_earthquake2/sp_earthquake2 |
| `School_SUB.txt` | `16E5DD11-C39F-4CD2-B80A-B48F518BA9A6` | `B5C0B422-E9C1-0F11-7424-46B7301891EC` | levels/sp_earthquake2/school_sub | levels/sp_earthquake2/sp_earthquake2 |
| `Solomon_Intro.txt` | `636BC355-00AF-4A0C-9714-4C4B43BD6899` | `083AD649-BF76-B628-BCA1-E602669C3F8F` | levels/sp_earthquake2/solomon_intro | levels/sp_earthquake2/sp_earthquake2 |
| `StagingArea_BIGPROPS.txt` | `82E7D2A5-2B5B-4477-A9D7-D161D42C7233` | `970428D0-1B7D-154B-A7B3-DC825DDA5C42` | levels/sp_earthquake2/stagingarea_bigprops | levels/sp_earthquake2/sp_earthquake2 |
| `StagingArea_SUB.txt` | `91B1E43F-5B21-47BA-8E8B-5DC2E900EC8C` | `B0160744-D0B3-6E76-5BD3-C6166B8955AA` | levels/sp_earthquake2/stagingarea_sub | levels/sp_earthquake2/sp_earthquake2 |

## SP_Finale（14 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Chase_SUB.txt` | `36678E4C-0570-43E1-B5BC-46FE998959C4` | `64EA9279-9954-4961-BD81-E6E72427219A` | levels/sp_finale/chase_sub | levels/sp_finale/sp_finale |
| `Credits.txt` | `F96BC97F-D271-497A-AC3E-7D8C3158B9C4` | `06CDE588-5AB8-E46E-A120-E4CEC36C9A57` | levels/sp_finale/credits | levels/sp_finale/sp_finale |
| `Escape_SUB.txt` | `BACD68D8-D3E1-4CBB-AC36-11E848B6A41D` | `13762E8D-3DC0-F5DC-0C18-D44D6AD9C109` | levels/sp_finale/escape_sub | levels/sp_finale/sp_finale |
| `Fight_SUB.txt` | `7DE02C96-C7FA-4176-9561-E1EEC57B031A` | `119CC2B6-D1E5-7CB4-7885-D38F2738401C` | levels/sp_finale/fight_sub | levels/sp_finale/sp_finale |
| `Level.txt` | `B4365122-0722-4E2B-A7D5-FDD4843EA551` | `3B4A79A9-B045-1F30-335F-893A7837A894` | levels/sp_finale/level | levels/sp_finale/sp_finale |
| `LightMap_01.txt` | `C822DA4D-0B3E-4ECA-93AD-08B5729363D4` | `ECFA255B-AC8A-88B9-01FA-D1A2F5100CC5` | levels/sp_finale/lightmap_01 | levels/sp_finale/sp_finale |
| `LightMap_02.txt` | `80F9D601-E74A-435F-8AFD-B7D2E92F4100` | `F54EDA05-0FA2-9912-ADDE-7F1CF27F30BB` | levels/sp_finale/lightmap_02 | levels/sp_finale/sp_finale |
| `LightMap_03.txt` | `35992C44-A6E9-4BAB-933C-8D352E0A0AF4` | `38A5F4A9-660B-9F24-F27B-C29CC2E68B8D` | levels/sp_finale/lightmap_03 | levels/sp_finale/sp_finale |
| `LightMap_04.txt` | `2554EF0E-D3B1-497C-B31C-DEA357A3470C` | `4FEC20A7-84D8-7827-F101-B89393A5B6B1` | levels/sp_finale/lightmap_04 | levels/sp_finale/sp_finale |
| `Penn_SUB.txt` | `13C20CB8-B2D3-43F8-8DE1-1904C0D1C868` | `1D24B936-8703-2128-47D1-93F6B3C6C919` | levels/sp_finale/penn_sub | levels/sp_finale/sp_finale |
| `SP_Finale.txt` | `8DA3322E-3E60-11E0-BFEE-95DA3EB52033` | `FA3D2D86-BD79-E903-5FF8-92C6B6AC4F47` | levels/sp_finale/sp_finale | levels/sp_finale/sp_finale |
| `SewerART_SUB.txt` | `09F7E85B-6366-4901-A305-5516C0D6275C` | `E0BEC42D-CCDF-7F79-4332-69C3BB31D631` | levels/sp_finale/sewerart_sub | levels/sp_finale/sp_finale |
| `Street_SUB.txt` | `F4B664F3-C960-4E88-9A98-EFD6D0B93D6C` | `DE8BC943-E194-DE96-EF3D-838382333D2B` | levels/sp_finale/street_sub | levels/sp_finale/sp_finale |
| `TrainRide_SUB.txt` | `6BDC8070-B40F-4E58-884C-31E1A98B5150` | `0CDAD375-7094-E0B3-3D70-28B612C0DF61` | levels/sp_finale/trainride_sub | levels/sp_finale/sp_finale |

## SP_Jet（13 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `ART_DogfightPartTwo_Backdrop.txt` | `0039EE5B-797A-4351-8743-5A2798D5D52D` | `B43411BD-5C68-6BDE-120A-340C776F30B2` | levels/sp_jet/art_dogfightparttwo_backdrop | levels/sp_jet/sp_jet |
| `Area_CarrierLanding.txt` | `0F4E713D-A763-41FF-9A5F-A21102254D04` | `AA6BD24D-9C54-CC83-56D3-3561DC001B22` | levels/sp_jet/area_carrierlanding | levels/sp_jet/sp_jet |
| `Area_Dogfight_1.txt` | `3CBB80B1-CF1C-4A08-AA9E-AC4346CDD782` | `C01AA4E0-6409-F3C5-14A6-19A11BD8F72D` | levels/sp_jet/area_dogfight_1 | levels/sp_jet/sp_jet |
| `Area_Dogfight_2.txt` | `4811B975-843F-4838-BF6F-F8E778F55C8E` | `46784A80-FBF6-A384-E99C-3201A9A477EA` | levels/sp_jet/area_dogfight_2 | levels/sp_jet/sp_jet |
| `Area_Fleet.txt` | `20E82312-D301-414C-BD07-8FF7073EEDDC` | `42B07D80-E748-3C48-64EA-1FCBCB4B9B03` | levels/sp_jet/area_fleet | levels/sp_jet/sp_jet |
| `Area_Going_Home.txt` | `A9172F6C-1366-4036-98D0-A787554F3B38` | `5B2518D3-1052-56E0-0F6E-A336BFF438DF` | levels/sp_jet/area_going_home | levels/sp_jet/sp_jet |
| `Area_Highway_Of_Death.txt` | `9FDA5BEC-DC9E-4054-B82B-D6637F8BA0B2` | `1F71794F-A1C6-0B46-CE51-C26588D736E2` | levels/sp_jet/area_highway_of_death | levels/sp_jet/sp_jet |
| `CarrierStart_playerAndWingmanAnimations.txt` | `4787890F-1EDD-4C9E-8714-FA4686D17D5C` | `A368C9D4-193F-5601-D236-A53C7E8F505C` | levels/sp_jet/carrierstart_playerandwingmananimations | levels/sp_jet/sp_jet |
| `Carrier_Details.txt` | `76D265C8-16E3-4DC7-9910-FF394ADE4075` | `F11DC4F3-EA0D-A0F5-4C93-E1814A1D58DF` | levels/sp_jet/carrier_details | levels/sp_jet/sp_jet |
| `Carrier_Interior.txt` | `D4EE8C6F-1BD3-4730-8717-C66EADCCC0F5` | `E6698DCD-F0A6-D8C9-B4B7-D06CE6B19DDD` | levels/sp_jet/carrier_interior | levels/sp_jet/sp_jet |
| `DogfightPartOne_Backdrop.txt` | `369CE8B2-4430-4B92-84CB-CA83B9F1374E` | `866B4C95-9D1F-3EBF-A723-FF36669FBDFC` | levels/sp_jet/dogfightpartone_backdrop | levels/sp_jet/sp_jet |
| `ParticleClouds.txt` | `38736F81-3952-4D1C-A918-79FE87EEB28A` | `316DC528-ADD7-4C0F-C9A1-BDD17B58EFAF` | levels/sp_jet/particleclouds | levels/sp_jet/sp_jet |
| `SP_Jet.txt` | `3C0DE194-B689-11DF-B8D0-D42ED28AF832` | `71CB3DFA-A864-643C-E2D5-89044ECB115B` | levels/sp_jet/sp_jet | levels/sp_jet/sp_jet |

## SP_New_York（5 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Level.txt` | `2D32E954-A1DB-4905-B533-670FFB6FA3F2` | `D16EF948-7A0A-61EF-EDED-F5C50D60ED2C` | levels/sp_new_york/level | levels/sp_new_york/sp_new_york |
| `LightMap_01.txt` | `8834A609-9127-46BD-AA59-0628C5707416` | `2FC37475-B913-4852-8D2F-77E9F631E341` | levels/sp_new_york/lightmap_01 | levels/sp_new_york/sp_new_york |
| `LightMap_02.txt` | `33369334-9C45-45E8-8BA2-48B09F5E6D56` | `487D16D4-80F2-C1C3-5BC8-4BC9C9980CE9` | levels/sp_new_york/lightmap_02 | levels/sp_new_york/sp_new_york |
| `SP_New_York.txt` | `936D5695-A989-4F39-B8C7-6404B0F55C5D` | `BEF855E9-584C-C802-2A03-C441228E42B9` | levels/sp_new_york/sp_new_york | levels/sp_new_york/sp_new_york |
| `TrainRide_SUB.txt` | `578CFBA0-221A-4651-8168-5B5645BAE92D` | `2542484D-BBEF-7B3C-4EC2-1AE0C537DDE4` | levels/sp_new_york/trainride_sub | levels/sp_new_york/sp_new_york |

## SP_Paris（25 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `BackdropBuildingsClose.txt` | `DE133D91-93A0-4953-9261-AFCC766DC627` | `4472A96A-DE64-273F-4542-55FD9E8C317B` | levels/sp_paris/backdropbuildingsclose | levels/sp_paris/sp_paris |
| `BackdropBuildingsFar.txt` | `935AA8D1-45CD-44F5-B844-529F2727ADBE` | `4D5265C1-7333-53B4-C5F3-D9DEAFA9D973` | levels/sp_paris/backdropbuildingsfar | levels/sp_paris/sp_paris |
| `Chase.txt` | `E8F78A6E-B093-4C3F-ADC4-6756795E1B72` | `F52362CC-1958-55F4-EA81-B66BC2C4EA7D` | levels/sp_paris/chase | levels/sp_paris/sp_paris |
| `ChaseIntro.txt` | `43C0B699-670F-49E1-B1D3-EAB513EA6341` | `0B524FA5-8A6C-D252-4B61-22BD7AF6ECCE` | levels/sp_paris/chaseintro | levels/sp_paris/sp_paris |
| `CorridorCorner.txt` | `1BB39846-A903-47FB-947E-716CF53ABD93` | `1C525E86-4C19-40A7-A829-31111215B00D` | levels/sp_paris/corridorcorner | levels/sp_paris/sp_paris |
| `CorridorSluice.txt` | `CDC11DC9-704C-4A35-9EA3-5D7E976F8773` | `070B67F1-9E08-C1DA-4562-C05473473007` | levels/sp_paris/corridorsluice | levels/sp_paris/sp_paris |
| `GasEventSluice.txt` | `080764B1-FE07-4A05-8134-821D30D7ECC8` | `A32EC3D8-8C54-6463-BF04-2A1E51474093` | levels/sp_paris/gaseventsluice | levels/sp_paris/sp_paris |
| `Heat.txt` | `A945175E-F943-4072-9070-304927394570` | `77573D81-ED54-936F-FA37-BC18955BA086` | levels/sp_paris/heat | levels/sp_paris/sp_paris |
| `Heat_PC_Only.txt` | `D23456F0-AB6D-4BC9-9CAA-01B76AE46B70` | `420BDCE0-BFB9-C8BC-9AE2-04BF756E3342` | levels/sp_paris/heat_pc_only | levels/sp_paris/sp_paris |
| `LightMap_01.txt` | `FD0C136E-1BCB-47E1-A7F2-CEACD93E4284` | `CF92BB9C-FEFC-918A-A032-0940F5B67BED` | levels/sp_paris/lightmap_01 | levels/sp_paris/sp_paris |
| `LightMap_02.txt` | `21FCF2DC-0CD1-4C34-B1AB-58E5D39F2910` | `0EAB6F5F-51D3-41AF-2D93-5BFD38B78B76` | levels/sp_paris/lightmap_02 | levels/sp_paris/sp_paris |
| `LightMap_03.txt` | `2CE2149D-0714-43B8-96EB-8D4B57E23E93` | `A26CFC0E-2780-9D05-FAF2-6595AD4A3DBB` | levels/sp_paris/lightmap_03 | levels/sp_paris/sp_paris |
| `Lobby.txt` | `B17CC92D-F9C5-4550-9BE0-14C978AA4885` | `1681B495-8C73-CE77-AE1B-128D4427AF7A` | levels/sp_paris/lobby | levels/sp_paris/sp_paris |
| `LowerOffice.txt` | `8943A5BA-6398-465D-B87C-DFC7B026EF5B` | `7828304F-15F3-7CD6-8664-93C479B1C093` | levels/sp_paris/loweroffice | levels/sp_paris/sp_paris |
| `LowerOffice_PC.txt` | `FDF3DFE7-292E-455F-B211-1174224A1D81` | `DDA89CC6-0BCB-F311-8059-093BC50610BB` | levels/sp_paris/loweroffice_pc | levels/sp_paris/sp_paris |
| `ParkingDeck.txt` | `9BD50745-82BB-4F10-83F5-FDD62F2A7D1F` | `CB062F45-0DEC-4AF4-D59D-63A0ABF18404` | levels/sp_paris/parkingdeck | levels/sp_paris/sp_paris |
| `ParkingDeckGate.txt` | `8F86F56A-8152-436D-888D-6AFF078B32D5` | `C8601A20-ABF2-0543-0A7C-6D17E04040CD` | levels/sp_paris/parkingdeckgate | levels/sp_paris/sp_paris |
| `ParkingDeckGate_PC.txt` | `CFCFE197-8797-431A-A0FA-1B6FC0631C12` | `5070C387-7C25-B478-3A5A-EC2D85A06B10` | levels/sp_paris/parkingdeckgate_pc | levels/sp_paris/sp_paris |
| `Rail.txt` | `A10BA099-8F8A-4A78-B02F-D875CD0521E2` | `976BAF07-6504-8F0B-F20E-778E4A8F04E7` | levels/sp_paris/rail | levels/sp_paris/sp_paris |
| `RailBackdrop.txt` | `7CF01CC7-75A0-4764-A658-5623A6F25BDB` | `988C2D21-38AA-667B-3C5A-9F68F36FD816` | levels/sp_paris/railbackdrop | levels/sp_paris/sp_paris |
| `SP_Paris.txt` | `61417F2E-BCD9-11DF-A157-A17CBD8140DE` | `33EB99A9-1251-E076-09DC-4771BE1DAEA5` | levels/sp_paris/sp_paris | levels/sp_paris/sp_paris |
| `Street.txt` | `34B71A4F-D285-48E7-BFBB-EBE029048E14` | `D657117C-D9C8-9A69-71C0-5C06BB7A76A1` | levels/sp_paris/street | levels/sp_paris/sp_paris |
| `TradingFloor.txt` | `B8F1865F-B174-400A-B788-04CE872B1F30` | `2FFDBAA2-C5A9-FA00-0598-BDF2EC5F5FB1` | levels/sp_paris/tradingfloor | levels/sp_paris/sp_paris |
| `UpperOffice.txt` | `D9D5D918-7655-4476-A608-9B50D575E5DC` | `EA6E874D-6395-8186-5BAD-D8BD400FBF8F` | levels/sp_paris/upperoffice | levels/sp_paris/sp_paris |
| `UpperOffice_PC.txt` | `56837FCD-3DB2-47DD-B74D-6A2CC7E1740D` | `266FCCC2-3D1D-E9C8-6C54-F172B52618FF` | levels/sp_paris/upperoffice_pc | levels/sp_paris/sp_paris |

## SP_Sniper（29 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `AlBashirStrike.txt` | `00270ED3-4AB5-4624-8B01-ED377DBD2400` | `2E3BEE0C-AC8F-A2C1-5E78-833BA278093C` | levels/sp_sniper/albashirstrike | levels/sp_sniper/sp_sniper |
| `AlBashirStrikeArt.txt` | `BFE704F4-A5AE-4AD7-B47D-1BF37E8B89B5` | `C3FF41D8-9C7B-F9EB-884F-46DE4D6C4056` | levels/sp_sniper/albashirstrikeart | levels/sp_sniper/sp_sniper |
| `AlBashirStrikeArt_PC.txt` | `68CD6727-AF03-4B93-841A-77A4EEA7EB91` | `7DC67491-47A4-B4F1-3630-ED5F6A09BC1F` | levels/sp_sniper/albashirstrikeart_pc | levels/sp_sniper/sp_sniper |
| `Background_01.txt` | `84426DA9-F386-4AAA-A769-216F7AD38820` | `1BE968C0-8D77-2BA0-2E92-E4DFD56DF889` | levels/sp_sniper/background_01 | levels/sp_sniper/sp_sniper |
| `Background_02.txt` | `F21013AD-E591-480E-A611-CF91B060E8EF` | `EFC49A15-8C73-8136-F53F-9644F6F5A90E` | levels/sp_sniper/background_02 | levels/sp_sniper/sp_sniper |
| `Background_Persistant.txt` | `4163D6B5-8642-4AD3-8030-1CCB79EA6BD3` | `38DBAD21-FE59-AC4D-42FF-1D7ED9A6EE37` | levels/sp_sniper/background_persistant | levels/sp_sniper/sp_sniper |
| `Backstreets.txt` | `EA7A5BD1-F1C7-4FAE-9177-CF4CC0532B7D` | `7D923AC5-99A7-86E0-D3FF-02727FA5B5BD` | levels/sp_sniper/backstreets | levels/sp_sniper/sp_sniper |
| `Briefing.txt` | `CE6E0A68-7377-4BD5-9ACF-0D14A755CAB5` | `58B1984D-5431-FA56-1C4E-82A6B6232123` | levels/sp_sniper/briefing | levels/sp_sniper/sp_sniper |
| `FailKnife.txt` | `2FE13C68-82F5-487A-AC00-790178BE5F5F` | `BB632F4A-8242-A6F0-79BD-5E4337BB4547` | levels/sp_sniper/failknife | levels/sp_sniper/sp_sniper |
| `Mall.txt` | `281F50A2-F5A5-4F5E-9F7D-304B0A197CCF` | `AD1020B1-6004-8218-C6A8-A8DF823E502F` | levels/sp_sniper/mall | levels/sp_sniper/sp_sniper |
| `MallDefence.txt` | `49C7FFB3-4DA6-45F3-8C5B-0A97E8C62FBE` | `686EB544-CAD6-78F1-89A7-2F8C42E2A3A4` | levels/sp_sniper/malldefence | levels/sp_sniper/sp_sniper |
| `MallDefence_Animation1.txt` | `FC616637-1C9D-40EE-8F6D-DC1C9EC7D120` | `EB1C866F-CDC2-4EB7-6401-EC46B6F37AA4` | levels/sp_sniper/malldefence_animation1 | levels/sp_sniper/sp_sniper |
| `MallDefence_Animation2.txt` | `A6C354E6-EAE4-48FB-A1AD-658B386DC1BE` | `49CF461B-870F-C198-D432-7C6824784384` | levels/sp_sniper/malldefence_animation2 | levels/sp_sniper/sp_sniper |
| `MallDefence_Animation3.txt` | `0C013DE2-6683-4274-87AD-0202A1F3D016` | `84F784B3-8D6F-9A57-6991-EFA10F537355` | levels/sp_sniper/malldefence_animation3 | levels/sp_sniper/sp_sniper |
| `MallDefence_Animation4.txt` | `E9A4EEE9-1078-4E70-9E2A-E44A34EDFF4A` | `199A56AB-C169-06BC-2674-DA9C6DE3281D` | levels/sp_sniper/malldefence_animation4 | levels/sp_sniper/sp_sniper |
| `MallDefence_Animation5.txt` | `2DD56B90-1243-45EF-BD5D-2FB2430359B5` | `0CC494BA-CA18-6643-6DB5-95DB51B2C9CA` | levels/sp_sniper/malldefence_animation5 | levels/sp_sniper/sp_sniper |
| `Mall_BehindStreet.txt` | `CB41242E-711E-4AA9-A4AA-28598ABB1E29` | `100AD991-6CAF-FD00-A0B7-3697F72E037F` | levels/sp_sniper/mall_behindstreet | levels/sp_sniper/sp_sniper |
| `Mall_Exterior.txt` | `ACA5C945-A87F-4F18-8D77-562E9830144B` | `46B41471-7FF4-D40D-E344-B32FFFC489FF` | levels/sp_sniper/mall_exterior | levels/sp_sniper/sp_sniper |
| `Mall_Exterior_PC.txt` | `2013FCA0-C501-4441-B09E-26A127E834C1` | `BEBD9485-7971-C51F-55B4-ADE4968649D2` | levels/sp_sniper/mall_exterior_pc | levels/sp_sniper/sp_sniper |
| `Mall_PC.txt` | `1437EF6C-6F8A-4053-A904-F4AEF100FF12` | `28DC2F24-30F2-56A2-B621-66385F46380B` | levels/sp_sniper/mall_pc | levels/sp_sniper/sp_sniper |
| `MannequinRoom.txt` | `5E947EEB-BFC4-4899-B3A7-39C120F0B78F` | `81CB17DF-136B-A280-08A2-9B61A4FEB9CA` | levels/sp_sniper/mannequinroom | levels/sp_sniper/sp_sniper |
| `Missile.txt` | `CB3D6F04-48F8-47E9-824A-EEEB5BF63C66` | `31DD51A9-E32B-9001-345C-4367E226C683` | levels/sp_sniper/missile | levels/sp_sniper/sp_sniper |
| `Overwatch.txt` | `18A7A2E0-BFC5-4EFC-8D6D-4CD6FA76DDB3` | `F66DBE5B-3488-C264-1A5A-367091C11D40` | levels/sp_sniper/overwatch | levels/sp_sniper/sp_sniper |
| `Plaza.txt` | `ACE972C8-1D0A-4C78-A913-99581F787DA0` | `31AF5685-B562-696B-EB5F-FEBF8C8C2D14` | levels/sp_sniper/plaza | levels/sp_sniper/sp_sniper |
| `ReconNest.txt` | `A4C82A7C-5751-45BE-99AC-57CFEE809A2C` | `B9A34906-94CA-BF01-1AA5-F52F40B44386` | levels/sp_sniper/reconnest | levels/sp_sniper/sp_sniper |
| `ReconNest_PC.txt` | `E6D612BB-0385-45B4-B5ED-6FD59A32AD0A` | `2885465D-FA0B-2336-95AC-3DFCADB2FCA2` | levels/sp_sniper/reconnest_pc | levels/sp_sniper/sp_sniper |
| `RocketApartment.txt` | `436AF208-7673-4DAB-942F-8BC8F1E956C6` | `DA3E2615-D9F8-DEC7-D839-946F929ECF45` | levels/sp_sniper/rocketapartment | levels/sp_sniper/sp_sniper |
| `SP_Sniper.txt` | `DBCE4061-E2A4-11DF-A647-FE6A1B285059` | `4AB0554F-5277-14FE-45C5-CD8C3E65344E` | levels/sp_sniper/sp_sniper | levels/sp_sniper/sp_sniper |
| `Sewers.txt` | `53C40C31-339A-4677-A446-A7B467EA82C4` | `E8F334BF-DD11-8CB5-44A6-DC89652E3532` | levels/sp_sniper/sewers | levels/sp_sniper/sp_sniper |

## SP_Tank（25 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Backdrop.txt` | `C6E3D0AE-52B7-4DE7-9996-A86F34311CD4` | `4C3B6ADF-8920-4ED1-FB91-70295C1349C7` | levels/sp_tank/backdrop | levels/sp_tank/sp_tank |
| `BankPlaza_01.txt` | `C6B7EE89-A89E-4E9B-9D8E-9487ED2C76E7` | `7B073BA8-6A43-F742-E63D-E164A1D29A63` | levels/sp_tank/bankplaza_01 | levels/sp_tank/sp_tank |
| `DesertFort.txt` | `44234CB8-700B-461D-AF51-4FD9555128A7` | `4C200C23-43D4-27E3-AC17-EBA1030EE457` | levels/sp_tank/desertfort | levels/sp_tank/sp_tank |
| `DesertFortPConly.txt` | `2B882A7B-FCFE-4807-8CAE-5EAB6F0225AC` | `06C313BF-7A57-1EA1-6C0E-84C4CC0F7B79` | levels/sp_tank/desertfortpconly | levels/sp_tank/sp_tank |
| `DesertFortSmallObjects_01_LevelArt.txt` | `8EE217B0-D011-42DA-9376-8FC00FAC6260` | `B3EED0F6-2951-1230-C556-79C9022DF614` | levels/sp_tank/desertfortsmallobjects_01_levelart | levels/sp_tank/sp_tank |
| `DesertIntro.txt` | `0F491108-2F72-47CB-8337-6AFBEB459AE6` | `BC490CCF-DE08-02FF-FB10-41D9A1367CBE` | levels/sp_tank/desertintro | levels/sp_tank/sp_tank |
| `DriveToBankPlaza_01.txt` | `85F2A766-9083-4F0F-A11D-CEE62AF439FE` | `A89EEE65-BA0D-4F3F-DD63-1C219A8A0F4E` | levels/sp_tank/drivetobankplaza_01 | levels/sp_tank/sp_tank |
| `DriveToBankPlaza_02.txt` | `1856E950-1702-4188-8B0F-A6C873A3B4BC` | `96EFA3A7-9D0B-915E-9692-9EAA7C184CB4` | levels/sp_tank/drivetobankplaza_02 | levels/sp_tank/sp_tank |
| `DriveToBankPlaza_03.txt` | `825D5256-4FA4-4468-9219-286E6A262D94` | `B907E3FE-47C4-FEB3-D808-08927F13B51A` | levels/sp_tank/drivetobankplaza_03 | levels/sp_tank/sp_tank |
| `DriveToBank_01_Substream_01.txt` | `8ECA7FCC-8176-44FA-ADD3-9E1AE7EA62AA` | `7CCF1B3D-AF29-1F72-4EF9-59464E230167` | levels/sp_tank/drivetobank_01_substream_01 | levels/sp_tank/sp_tank |
| `DriveToBank_01_Substream_02.txt` | `7C080526-B202-4F83-B6A9-0D524AD470EF` | `0BA72B7F-1298-814C-C238-3E9BCEB1ABB9` | levels/sp_tank/drivetobank_01_substream_02 | levels/sp_tank/sp_tank |
| `DriveToBank_01_Substream_03.txt` | `324062A9-EA68-47C3-B997-E0883EB2EA8E` | `553676D7-B014-4743-9CE6-BE68D4CBCB62` | levels/sp_tank/drivetobank_01_substream_03 | levels/sp_tank/sp_tank |
| `DriveToBank_02_Substream_01.txt` | `F3BAEF58-3D73-4E03-8453-BDD846FCE832` | `FE8A4835-739C-6EE4-5295-5ACA68528703` | levels/sp_tank/drivetobank_02_substream_01 | levels/sp_tank/sp_tank |
| `DriveToBank_02_Substream_02.txt` | `FC020BDB-ADA4-4AFD-9F9A-7118DED6CD1E` | `F970B20E-E62A-4377-0EC3-DB98D63F119B` | levels/sp_tank/drivetobank_02_substream_02 | levels/sp_tank/sp_tank |
| `HighWayOverpass_01_LevelArt_Substream_01.txt` | `3E9E2A91-4ABA-4D70-BB5D-A1BB4AF71A17` | `1D09862D-8284-D213-C0EB-2D7FB1F779F7` | levels/sp_tank/highwayoverpass_01_levelart_substream_01 | levels/sp_tank/sp_tank |
| `HighwayOfDeath.txt` | `C6FEE734-0FBC-475A-8773-16CEE51596D0` | `BC8DC981-4625-2355-04E5-B326F548D0E6` | levels/sp_tank/highwayofdeath | levels/sp_tank/sp_tank |
| `HighwayOfDeath2.txt` | `B2CC7F28-F5E8-43D1-B6CE-7384EA7E2EB1` | `7DB4EA02-57ED-CA63-614D-CEECEB11D4AB` | levels/sp_tank/highwayofdeath2 | levels/sp_tank/sp_tank |
| `HighwayOverpass_01.txt` | `8709713A-D295-4774-A81C-5339CB593165` | `A0940976-5CE9-AC53-8EAC-F31DBAF941A7` | levels/sp_tank/highwayoverpass_01 | levels/sp_tank/sp_tank |
| `HighwayToTeheran_01.txt` | `2E9745C5-A3FB-4233-94BD-C10A2E310742` | `A79DA040-87B2-4070-F611-89CF52DFB62C` | levels/sp_tank/highwaytoteheran_01 | levels/sp_tank/sp_tank |
| `HighwayToTeheran_02.txt` | `067A80BA-0A19-40E1-9819-50CEF742387A` | `EF50CD8A-A5E7-40A2-0673-B1D8D23AC5F2` | levels/sp_tank/highwaytoteheran_02 | levels/sp_tank/sp_tank |
| `MICLIC-HighwayToTeheran.txt` | `43B5EA51-153F-4314-BE3C-E10355CB340C` | `F81E4AF3-E614-1CC1-1875-7AAA7EFD5354` | levels/sp_tank/miclic-highwaytoteheran | levels/sp_tank/sp_tank |
| `MICLIC.txt` | `12045EDE-2A4E-41ED-AEA1-5643CF1BF1B2` | `4FC725F5-4B1B-ECE4-21FF-D05FB4FFAC87` | levels/sp_tank/miclic | levels/sp_tank/sp_tank |
| `MICLICArt.txt` | `D1573748-690C-44F0-B593-3AAA1A53F3EC` | `8214CD06-B994-1696-65C3-EA8442686DA5` | levels/sp_tank/miclicart | levels/sp_tank/sp_tank |
| `RoadToDesert_01.txt` | `695D87A7-C6D5-48E8-BB58-76E8B33EE739` | `DA6CEDC4-01F7-D27B-6CC1-2B97E5F3AB23` | levels/sp_tank/roadtodesert_01 | levels/sp_tank/sp_tank |
| `SP_Tank.txt` | `A263A077-CA17-11DF-830F-E4337AA80D37` | `67F82662-BE3A-5161-E910-DACF2075AB01` | levels/sp_tank/sp_tank | levels/sp_tank/sp_tank |

## SP_Tank_b（15 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Ambush.txt` | `26231680-F5A9-4707-9061-CD30F78422AD` | `C47EF75E-7B71-3264-471D-7EC40C19A64B` | levels/sp_tank_b/ambush | levels/sp_tank_b/sp_tank_b |
| `BankPlazaBackdrop.txt` | `562ED34A-AF72-486E-B266-28A4ECC9FE0E` | `E02CAA61-7CBB-A3DE-5BA0-D22C214F4875` | levels/sp_tank_b/bankplazabackdrop | levels/sp_tank_b/sp_tank_b |
| `BankPlaza_01.txt` | `23D6C3B1-ED6D-4D1F-B040-6369F32FC010` | `670E35B7-1C9B-1E29-5CF1-A5CC5815DBAC` | levels/sp_tank_b/bankplaza_01 | levels/sp_tank_b/sp_tank_b |
| `BlockedStreet.txt` | `217A8C39-9D83-4913-BA92-E3A66FEEA862` | `3E4078F2-A6F6-6292-3262-C1062BD5B45C` | levels/sp_tank_b/blockedstreet | levels/sp_tank_b/sp_tank_b |
| `BlockedStreet2.txt` | `173FF943-634A-4E1C-8DD3-ED5A19E7DD32` | `A449C0AA-DA48-27D1-FB0C-30A3DA7B8B14` | levels/sp_tank_b/blockedstreet2 | levels/sp_tank_b/sp_tank_b |
| `DriveThrough.txt` | `1DFFB784-3BAF-422D-910E-F023D2D599BA` | `56CBD10B-2764-87E3-D1D1-F2AD0B2FA695` | levels/sp_tank_b/drivethrough | levels/sp_tank_b/sp_tank_b |
| `DriveToBankPlaza_01.txt` | `5F90891F-9023-4BE2-9D75-1F0B1898CC2C` | `E94A3A2C-1D6C-2F6E-E574-158D788E7E67` | levels/sp_tank_b/drivetobankplaza_01 | levels/sp_tank_b/sp_tank_b |
| `DriveToBankPlaza_03.txt` | `BA50B396-D584-4C75-A417-B7F4A2D8A580` | `682C3685-43E6-0F0C-0C13-1F3B64C998F0` | levels/sp_tank_b/drivetobankplaza_03 | levels/sp_tank_b/sp_tank_b |
| `IntroRail.txt` | `E444CF7F-5FD1-4BAD-A48B-407ADE926571` | `A101D95D-B659-3BEE-2B22-172D66538D74` | levels/sp_tank_b/introrail | levels/sp_tank_b/sp_tank_b |
| `LightMap_01.txt` | `642E2BA7-F618-4713-9BC9-22A5BA684523` | `0D807DA2-0B8B-0AEF-D501-3DFE3D04B494` | levels/sp_tank_b/lightmap_01 | levels/sp_tank_b/sp_tank_b |
| `LightMap_02.txt` | `577CE277-2124-4009-838C-C395BB5FBB97` | `4A67EA1E-BDD5-7BCD-78FC-3F9FD1C67EB4` | levels/sp_tank_b/lightmap_02 | levels/sp_tank_b/sp_tank_b |
| `LightMap_03.txt` | `EF63A9C3-5981-45F9-9DCE-BB0974B58636` | `E7082B41-AC84-66F4-91FF-3D777B761022` | levels/sp_tank_b/lightmap_03 | levels/sp_tank_b/sp_tank_b |
| `Outroscene.txt` | `10868833-9AF9-4C51-9457-439032DC9AAB` | `BC567706-BE96-0E73-FF7A-3CFB57CB07B9` | levels/sp_tank_b/outroscene | levels/sp_tank_b/sp_tank_b |
| `SP_Tank_b.txt` | `7662E9AF-091E-4A19-B7ED-751D083E7693` | `0717DF61-6F12-6D33-E820-A1F76E42B703` | levels/sp_tank_b/sp_tank_b | levels/sp_tank_b/sp_tank_b |
| `SideStreet.txt` | `2743BED8-F3D4-4873-96D6-05555275D314` | `8AA16BFF-A323-F268-C788-504B30E37BAA` | levels/sp_tank_b/sidestreet | levels/sp_tank_b/sp_tank_b |

## SP_Valley（25 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Airdrop.txt` | `E1933E55-0E4A-47A2-8C54-D51B04195BC9` | `663A17FE-2D8D-8430-A595-A3AA7B0E4943` | levels/sp_valley/airdrop | levels/sp_valley/sp_valley |
| `AmbientWar.txt` | `A86B7EEF-7A64-44B2-B912-1140A33994A6` | `E3DE6D04-8B21-C820-E6AD-DF6B2EAB20AC` | levels/sp_valley/ambientwar | levels/sp_valley/sp_valley |
| `BriefingOnHill.txt` | `E8D8FAF0-3F9B-4ED9-B4C3-6956CD1923D6` | `78E75AF5-8682-B03A-C50A-9C390CC648F7` | levels/sp_valley/briefingonhill | levels/sp_valley/sp_valley |
| `Forest.txt` | `49B2BD9D-9876-4059-8F6D-8A300DE35B58` | `CF5AE7B9-E263-458C-53F5-16A4CA774B8B` | levels/sp_valley/forest | levels/sp_valley/sp_valley |
| `ForestArt.txt` | `161C254F-1BCE-4291-A9C5-81C0A5F28503` | `9D6EBB20-DE8D-B3FA-BF19-A1C4F472AA8E` | levels/sp_valley/forestart | levels/sp_valley/sp_valley |
| `Hillside.txt` | `2660E458-E4AF-4BA7-A632-00BDF0949119` | `BE7F4499-EB3D-B593-1959-B51D115F8126` | levels/sp_valley/hillside | levels/sp_valley/sp_valley |
| `Ridge.txt` | `88955F29-0B25-423C-9671-E363B86B68DF` | `CE6B11C2-002A-FF52-8290-F00B86E71283` | levels/sp_valley/ridge | levels/sp_valley/sp_valley |
| `RunDownHill.txt` | `A4440749-E087-4A2F-85BB-94510E0835DF` | `17196179-0B6C-BF10-1408-11A7FF79573E` | levels/sp_valley/rundownhill | levels/sp_valley/sp_valley |
| `SP_Valley.txt` | `9B6EE657-5639-4A04-AA88-16E9E201806E` | `CEDC393F-3DDC-A9C1-5CD1-E186790CE053` | levels/sp_valley/sp_valley | levels/sp_valley/sp_valley |
| `Valley.txt` | `058192DB-73BF-4527-84B9-EDD6F2CCE7A4` | `75A462B3-D54C-9190-FAE1-E9D79CAF4794` | levels/sp_valley/valley | levels/sp_valley/sp_valley |
| `ValleyAdvanceToBridge.txt` | `3F4E5D72-E14D-46E0-9D7A-992C15326C24` | `FC849ED6-8E1B-9663-636B-0D659A68D667` | levels/sp_valley/valleyadvancetobridge | levels/sp_valley/sp_valley |
| `ValleyArt.txt` | `D34CFDC5-FDD2-4857-B700-5189DAE5D292` | `B824D99C-DF36-F08F-C6C7-ADD52B42003E` | levels/sp_valley/valleyart | levels/sp_valley/sp_valley |
| `ValleyArtilleryCamp.txt` | `D8D4C725-0729-4683-90C3-03E92ABF8156` | `0D02A200-5638-F454-6071-4C9E9CBE628A` | levels/sp_valley/valleyartillerycamp | levels/sp_valley/sp_valley |
| `ValleyField1.txt` | `49D41D35-7C70-4C55-99A5-100B321F832D` | `84B9FC2B-5BD2-56D6-434C-5047CF48BB90` | levels/sp_valley/valleyfield1 | levels/sp_valley/sp_valley |
| `ValleyField2.txt` | `11A55481-AAA5-4F37-9AE6-30DE7AFF4252` | `AF38287A-E37F-D644-1241-1FDDDEE9FE8D` | levels/sp_valley/valleyfield2 | levels/sp_valley/sp_valley |
| `ValleyJet.txt` | `9F4A57A6-35CA-4E06-BDB9-419F5F0D44AE` | `8ECD6A8D-175B-BD86-276F-25FE418B2786` | levels/sp_valley/valleyjet | levels/sp_valley/sp_valley |
| `ValleyJetBriefing.txt` | `12C1BE23-485F-487D-A61D-82DDB6861585` | `D774F880-216A-1757-EE8A-44ABFA2E6426` | levels/sp_valley/valleyjetbriefing | levels/sp_valley/sp_valley |
| `ValleyJet_EndScene.txt` | `0E819F39-BE3D-438E-93C0-468706F5442A` | `BC5804A2-A13A-A052-771A-6F7BACB945A0` | levels/sp_valley/valleyjet_endscene | levels/sp_valley/sp_valley |
| `ValleyTankBattle.txt` | `E1860923-60AB-45C9-BCE0-117948440820` | `373324FF-ED07-3BA7-C0F0-648E66026E63` | levels/sp_valley/valleytankbattle | levels/sp_valley/sp_valley |
| `ValleyTankBriefing.txt` | `808F42F4-8300-432C-978F-ED71EBEBE609` | `389E1444-93EF-F428-A06E-490118BB0524` | levels/sp_valley/valleytankbriefing | levels/sp_valley/sp_valley |
| `Zone1.txt` | `84D4FFAD-8C79-44DA-A1D6-ACDDC79F80AB` | `C5EB6429-F007-0481-11BB-F708825C9520` | levels/sp_valley/zone1 | levels/sp_valley/sp_valley |
| `Zone2.txt` | `AC685F79-A761-42DC-9776-17F5D4DB1F23` | `16EF6D47-B6A7-EC85-E58F-6E4793B50492` | levels/sp_valley/zone2 | levels/sp_valley/sp_valley |
| `Zone3.txt` | `24237FC1-8032-48EE-A694-27719D88E357` | `57C4E23D-50B9-4489-82F2-7763C6429ADF` | levels/sp_valley/zone3 | levels/sp_valley/sp_valley |
| `Zone4.txt` | `A5EEA052-43B9-403C-BF3E-6D802E66BEA7` | `A0BAC385-CDD2-CE2B-C14E-12BC9F0DD1EF` | levels/sp_valley/zone4 | levels/sp_valley/sp_valley |
| `Zone5.txt` | `601C2215-91B4-4596-AD79-D185A9CF934E` | `FCB8C901-8E36-C35D-6539-A838B92D6FD6` | levels/sp_valley/zone5 | levels/sp_valley/sp_valley |

## SP_Villa（26 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Background.txt` | `F749441A-8971-4946-B147-397CB6F1A85B` | `AA481C32-952C-BE32-6F60-6D4E213250D0` | levels/sp_villa/background | levels/sp_villa/sp_villa |
| `Basement.txt` | `8988D551-8CAA-459D-8D63-6C1976FC1138` | `44A043A8-9A9A-A65F-C1CD-9C6E189C2729` | levels/sp_villa/basement | levels/sp_villa/sp_villa |
| `Blackburn.txt` | `33637737-AE78-4C1A-B1DE-F9952CDCB3FD` | `74FB4941-4688-C507-18E1-D742632872E3` | levels/sp_villa/blackburn | levels/sp_villa/sp_villa |
| `Chopper.txt` | `547B4CC4-E654-44FC-9198-E64686EBD430` | `45936AC0-B0E6-9E10-D074-F1F07AD7B251` | levels/sp_villa/chopper | levels/sp_villa/sp_villa |
| `Drive.txt` | `F01F2D5B-3C51-43A9-A6C1-74FD2EC2FBF4` | `E0067531-456F-9159-0035-50070FA051BA` | levels/sp_villa/drive | levels/sp_villa/sp_villa |
| `Drive_2.txt` | `E8D4462E-AB80-49CD-BCE3-B27DBF8278D5` | `BB0547A9-23C8-F39A-3D9D-393B7227A9C9` | levels/sp_villa/drive_2 | levels/sp_villa/sp_villa |
| `Drive_PC.txt` | `635FF876-9AFB-41F7-BF2F-071FCE9A1B57` | `E56CF861-F8FD-2E89-1487-78E52A236D75` | levels/sp_villa/drive_pc | levels/sp_villa/sp_villa |
| `Garden.txt` | `B82A6F46-14AD-446E-8A1E-46FB03D19610` | `0CA867A4-1F8D-E99D-0D4E-763B239A74F5` | levels/sp_villa/garden | levels/sp_villa/sp_villa |
| `Garden_PC.txt` | `E2FCA80C-70F1-4466-8A4D-15A5616B5F1B` | `8FCEF965-FF05-6F29-82E4-89412B5DC44F` | levels/sp_villa/garden_pc | levels/sp_villa/sp_villa |
| `GateHouse.txt` | `1934EC11-D3CF-41B3-939D-1E99364C1920` | `9C99DF8B-B297-27AD-C644-1FA844924DF7` | levels/sp_villa/gatehouse | levels/sp_villa/sp_villa |
| `Halo.txt` | `687D6B21-EFB7-496E-8573-A02102E8B965` | `72E0DE16-B076-0820-18D4-5E7787E99BB8` | levels/sp_villa/halo | levels/sp_villa/sp_villa |
| `Halo_Backdrop.txt` | `C95FE042-00EA-47AF-98C2-F545013A66F3` | `20ADC2B1-37D5-22BF-EDA8-FEA0D3F0C864` | levels/sp_villa/halo_backdrop | levels/sp_villa/sp_villa |
| `Landing.txt` | `1CE226F4-17AC-4DC2-810A-E0899E22ED0B` | `49C7DB9D-C2A4-DB0B-4E84-D0FE5701BA7F` | levels/sp_villa/landing | levels/sp_villa/sp_villa |
| `Lightmap_01.txt` | `623975E7-E434-447F-8FBB-A6262DD1E9C7` | `5C66586D-5345-562F-5920-9E05E054BD5F` | levels/sp_villa/lightmap_01 | levels/sp_villa/sp_villa |
| `Lightmap_02.txt` | `2FFEA4C0-B08F-4226-87C5-D741C0D7A472` | `E9896092-501A-722A-E668-32A04CC5800C` | levels/sp_villa/lightmap_02 | levels/sp_villa/sp_villa |
| `Lightmap_03.txt` | `4B11EEBB-74A9-4E3E-B289-5B8B37C693F6` | `9C7E0D15-2E1D-2A4D-2038-CA517EEC6D28` | levels/sp_villa/lightmap_03 | levels/sp_villa/sp_villa |
| `Lightmap_Cutscene01.txt` | `9487719F-DAAE-429A-A849-A124C17548DB` | `8D4AF35D-DB3F-BEE5-130C-B685CB9B4EF9` | levels/sp_villa/lightmap_cutscene01 | levels/sp_villa/sp_villa |
| `Lightmap_Cutscene02.txt` | `CA392F7F-2370-4A92-8126-47871FD8D94C` | `ABC50C7E-F126-1C2C-A68B-88B82F06D745` | levels/sp_villa/lightmap_cutscene02 | levels/sp_villa/sp_villa |
| `Poolhouse.txt` | `0F934885-455D-43D4-8188-A5C387263A69` | `161A4648-8B2F-F840-947A-CDE4FF2BDB5D` | levels/sp_villa/poolhouse | levels/sp_villa/sp_villa |
| `Poolhouse_Extra.txt` | `5B213131-EE0E-437A-9C9E-ED719169DDC8` | `E668C95B-02FE-5142-1CA2-19B6D587638B` | levels/sp_villa/poolhouse_extra | levels/sp_villa/sp_villa |
| `Rail.txt` | `C6753483-91D3-4718-AEAD-3E60D6074210` | `7839231F-7A1F-D622-8C73-EE951B129ED0` | levels/sp_villa/rail | levels/sp_villa/sp_villa |
| `RailSUV.txt` | `07132115-00D5-4D91-886F-9B275021D55F` | `05C82B30-EFED-EFBC-8954-338F7F62E120` | levels/sp_villa/railsuv | levels/sp_villa/sp_villa |
| `SP_Villa.txt` | `6B420080-18CB-11E0-B456-BF5782883243` | `383F2AC9-94BF-286D-587A-27594550D561` | levels/sp_villa/sp_villa | levels/sp_villa/sp_villa |
| `Villa.txt` | `DD693670-3EDD-448C-8CD3-1463B234E44C` | `2FEFEDB2-EDA4-2353-33F2-D77E57EBF5BE` | levels/sp_villa/villa | levels/sp_villa/sp_villa |
| `Villa_Extra.txt` | `387A11A6-2017-4C74-9509-A9EE0140B290` | `C436D6F4-8874-C951-AEE3-66AC5838BAAF` | levels/sp_villa/villa_extra | levels/sp_villa/sp_villa |
| `Villa_PC.txt` | `6FF867EF-5C65-41B3-8836-2DAD7CE63522` | `27A4D318-0C1B-AA64-8A84-5E4B8E125C0E` | levels/sp_villa/villa_pc | levels/sp_villa/sp_villa |

## Web_Loading（1 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Web_Loading.txt` | `6F1BF9BC-9D7E-11E0-B6E2-B72F04A03239` | `6092CB78-2093-C04B-4DFD-C19D7B0B8597` | levels/web_loading/web_loading | levels/web_loading/web_loading |

## XP1_001（8 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `CQ_S1.txt` | `804D7CF1-7131-4CA3-8690-A3CE12E3ADE7` | `2725E329-51B0-C4DF-9564-AEF37D8020BE` | levels/xp1_001/cq_s1 | levels/xp1_001/xp1_001 |
| `Conquest_Large.txt` | `7BDBDA41-14C2-497C-BE3A-E6EBDDEED918` | `808DA917-89C5-324C-78D3-7B5B366FC0B5` | levels/xp1_001/conquest_large | levels/xp1_001/xp1_001 |
| `Conquest_Small.txt` | `60393B97-9B67-47D0-982E-0EB55BDA2BE7` | `3A1187F3-0401-A1F9-A4ED-B95F1389FF2D` | levels/xp1_001/conquest_small | levels/xp1_001/xp1_001 |
| `Rush.txt` | `41A72DEB-7EEC-438F-9D3A-A757BC1FC436` | `C9083E4A-F081-417A-3164-C8EC7380667F` | levels/xp1_001/rush | levels/xp1_001/xp1_001 |
| `SquadDeathmatch.txt` | `531ED49C-6AB9-42C5-ACA3-E344319FE0E3` | `F6638E09-7F50-FE79-ADB1-352F0CEBBF0F` | levels/xp1_001/squaddeathmatch | levels/xp1_001/xp1_001 |
| `SquadRush.txt` | `E6BE14AC-69B2-4740-8312-76BB4B51DA5E` | `20123ED8-C726-CDB0-6281-F552600A0815` | levels/xp1_001/squadrush | levels/xp1_001/xp1_001 |
| `TDM.txt` | `38FF761F-FCCB-4BF3-ADFE-0E9093A78382` | `DC682EDD-C2C5-170E-7BB4-375381ED1459` | levels/xp1_001/tdm | levels/xp1_001/xp1_001 |
| `XP1_001.txt` | `FAF35F00-5263-40A3-AB4D-67384BC2AD6D` | `FFF10E3D-A4EB-0F3C-13D5-E665BAA27629` | levels/xp1_001/xp1_001 | levels/xp1_001/xp1_001 |

## XP1_002（8 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `CQ_L.txt` | `CAA9CDD7-9F33-4D1F-BBFD-387AA23E2A5D` | `F66E2DF3-FD5C-21D5-B577-99708D11B3CA` | levels/xp1_002/cq_l | levels/xp1_002/xp1_002 |
| `CQ_S.txt` | `BA57F26B-896D-4745-80EC-2148AA4FABED` | `4CA67086-4270-BDEC-C570-A5A709959189` | levels/xp1_002/cq_s | levels/xp1_002/xp1_002 |
| `CQ_S1.txt` | `ED52B454-036B-4CE4-9E3D-7F07529F14C0` | `4994F319-538E-74B7-C862-D45C299EB82A` | levels/xp1_002/cq_s1 | levels/xp1_002/xp1_002 |
| `R.txt` | `09B59E2B-1A83-4CF8-8706-E9369B0829C3` | `E1CDBA58-14CA-BD1B-876C-186DCB654659` | levels/xp1_002/r | levels/xp1_002/xp1_002 |
| `SQDM.txt` | `FFBD6B8C-7C3C-4017-9E07-6659D74315F1` | `0D5AA962-C94A-F818-F55B-C49E671815C5` | levels/xp1_002/sqdm | levels/xp1_002/xp1_002 |
| `SR.txt` | `6A93D11E-A0F5-41A3-AF73-DB497A849981` | `6B3BD074-2621-A9D4-CAC4-EB24A713A27E` | levels/xp1_002/sr | levels/xp1_002/xp1_002 |
| `TDM.txt` | `50AA586A-DF7E-4044-B186-A9C7B7948841` | `5BA45AFD-07CD-09DE-94B5-2BE176AA80A1` | levels/xp1_002/tdm | levels/xp1_002/xp1_002 |
| `XP1_002.txt` | `D658DDB6-0B1E-4555-ABB8-5BC931C48F16` | `AF97F399-DDF1-6A91-0B22-3BB2E844C130` | levels/xp1_002/xp1_002 | levels/xp1_002/xp1_002 |

## XP1_003（8 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `CQ_L.txt` | `835767FE-793D-48ED-9777-EDDCC41CB0E8` | `C45719A1-AC0B-9344-DEE2-BB9E137BC3D7` | levels/xp1_003/cq_l | levels/xp1_003/xp1_003 |
| `CQ_S.txt` | `788CAC26-FDA1-4EE6-9598-16E3DEA58535` | `CDE50BB6-A595-3A6F-C2C5-0897F9143BC5` | levels/xp1_003/cq_s | levels/xp1_003/xp1_003 |
| `CQ_S1.txt` | `CC8B1D4D-6847-43CC-8C3A-96BC678D414F` | `35817BD1-09DE-F97D-7187-849370612C35` | levels/xp1_003/cq_s1 | levels/xp1_003/xp1_003 |
| `R.txt` | `0444513F-58EE-4C87-B5A7-7E07E110A97A` | `C27FF7FA-FED7-F172-61C3-66A8B5F92751` | levels/xp1_003/r | levels/xp1_003/xp1_003 |
| `SQDM.txt` | `BA62DE57-2F93-45DA-A6B2-23A5EC90A95D` | `6DD5E604-2F31-6408-AD6B-66945443B3AD` | levels/xp1_003/sqdm | levels/xp1_003/xp1_003 |
| `SR.txt` | `F4717AC7-4469-45C6-85C1-794A7E74A937` | `6941151B-26C4-77E4-2FE1-21D1A97D5D3C` | levels/xp1_003/sr | levels/xp1_003/xp1_003 |
| `TDM.txt` | `951E1917-19AD-4803-87D3-0E5703367366` | `AA9F7FF7-3128-B092-ED17-4E2B244EF3A2` | levels/xp1_003/tdm | levels/xp1_003/xp1_003 |
| `XP1_003.txt` | `DB9EABAF-924A-4183-8AE6-D4C6E7A016EF` | `F7593D4F-5901-81AE-4862-018A719FDAFE` | levels/xp1_003/xp1_003 | levels/xp1_003/xp1_003 |

## XP1_004（7 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `CQ_L.txt` | `B90BFAC2-68E8-4455-BF20-1128B2CAC804` | `C7039B02-0415-6F1C-C65A-59A89432C783` | levels/xp1_004/cq_l | levels/xp1_004/xp1_004 |
| `CQ_S.txt` | `6C5E1DF6-B428-4A11-BA06-15E565B63802` | `A44167A2-B0D1-3EA5-C4DD-517FD23EC6A2` | levels/xp1_004/cq_s | levels/xp1_004/xp1_004 |
| `R.txt` | `2EE027C6-21B3-437D-B1C5-5F318B02CD3C` | `A9DEB9E6-D322-4527-6A2D-0A4023BED048` | levels/xp1_004/r | levels/xp1_004/xp1_004 |
| `SQDM.txt` | `C0ECF48A-F9D2-4791-B24E-F00D4B5D20C6` | `242294F9-3ACE-2455-A91D-5180653311E8` | levels/xp1_004/sqdm | levels/xp1_004/xp1_004 |
| `SR.txt` | `71C03386-0EFC-4233-B1AE-2A73EC74F17B` | `C1A5676D-1AA9-4CEE-4EB0-1DE2835B238B` | levels/xp1_004/sr | levels/xp1_004/xp1_004 |
| `TDM.txt` | `B0B01D8B-514D-45BA-B28C-7F5C881928D4` | `16DB2D0A-4650-631C-6BC6-2A061450FC72` | levels/xp1_004/tdm | levels/xp1_004/xp1_004 |
| `XP1_004.txt` | `12F3EC6B-A63A-4B0C-B0CA-68A4A3B13E28` | `DE1B0E42-2FA7-AF09-04B7-263495B28631` | levels/xp1_004/xp1_004 | levels/xp1_004/xp1_004 |

## XP2_Factory（6 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `DOM2.txt` | `A40E86D4-FAC2-4F44-B466-65EBC5D70838` | `6376988E-8B5F-E55A-6D4F-4A525A7149E9` | levels/xp2_factory/dom2 | levels/xp2_factory/xp2_factory |
| `Deathmatch.txt` | `1C050CA7-CEA6-46F1-805F-FC43F345A675` | `155994EA-EDD7-0C6A-644F-4F9BBACAAC68` | levels/xp2_factory/deathmatch | levels/xp2_factory/xp2_factory |
| `GunMaster.txt` | `71BE4812-9854-4699-AE73-A89D746EADF0` | `F1CD5124-86BD-8BD6-F29F-37E3D2395AB0` | levels/xp2_factory/gunmaster | levels/xp2_factory/xp2_factory |
| `SQDM.txt` | `E02CED22-502E-4FD4-A525-EE6491DA3682` | `1CFB59DC-2E4E-6617-37D5-F565FB4AA9A8` | levels/xp2_factory/sqdm | levels/xp2_factory/xp2_factory |
| `TDM.txt` | `E085D201-B547-4A3A-BA21-CFA27398E3C6` | `3A589A57-3411-A3B8-6BDC-6CA7C9F8B765` | levels/xp2_factory/tdm | levels/xp2_factory/xp2_factory |
| `XP2_Factory.txt` | `BE1400B9-1129-11E1-95E8-C76B83E5975F` | `7B30CA53-98C8-C798-7F60-BFA25CA17925` | levels/xp2_factory/xp2_factory | levels/xp2_factory/xp2_factory |

## XP2_Office（6 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `DeathMatch.txt` | `0E79A42A-B9BD-4D09-BF80-B408EC35D979` | `7D3D985E-C0D1-4CB0-459F-B11C35A1F320` | levels/xp2_office/deathmatch | levels/xp2_office/xp2_office |
| `Domination.txt` | `926E20E2-E153-44A4-BCF3-25C531DAE1C0` | `E54203F2-0FEF-5DA9-CF2D-E08529C5CD44` | levels/xp2_office/domination | levels/xp2_office/xp2_office |
| `GunMaster.txt` | `EF46ECF0-5581-4E08-B8DF-B2248408804B` | `363FBBF7-E799-CE57-4002-D4976E4B299A` | levels/xp2_office/gunmaster | levels/xp2_office/xp2_office |
| `SQDM.txt` | `2918D2D5-EE0F-42DD-9AEC-AD16F8901751` | `CF1F891F-0293-D2E1-8A58-3E252D1DE80E` | levels/xp2_office/sqdm | levels/xp2_office/xp2_office |
| `TeamDeathMatch.txt` | `4739D51F-556F-4A07-B357-CB0DD4DCF71F` | `0568A773-67C4-FCFA-81EB-6E360EFF1EB5` | levels/xp2_office/teamdeathmatch | levels/xp2_office/xp2_office |
| `XP2_Office.txt` | `7891CA9C-41C1-11E1-BC78-C1265BEA77C6` | `B07CF1A7-0FD7-D068-A245-B43970082956` | levels/xp2_office/xp2_office | levels/xp2_office/xp2_office |

## XP2_Palace（6 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `DeathMatch.txt` | `539DDFA9-2974-41DA-B571-4D6F5277F79E` | `3B02457F-2629-10D3-DD01-46FD78FD9041` | levels/xp2_palace/deathmatch | levels/xp2_palace/xp2_palace |
| `Domination.txt` | `A61362A1-5A29-461D-920E-B73C8FC7634F` | `AFFD15BA-09DE-D1FA-0384-15D5B129CE5C` | levels/xp2_palace/domination | levels/xp2_palace/xp2_palace |
| `GunMaster.txt` | `E43996A3-CCFF-41D9-9240-2281200AE97B` | `5061BC1B-2A1C-93A9-76C6-02FEF8AC53E7` | levels/xp2_palace/gunmaster | levels/xp2_palace/xp2_palace |
| `SquadDeathmatch.txt` | `62789FB8-C7A1-49ED-93D5-F58AF1967BF1` | `9CD9E2FF-99C4-1D78-B14C-82330ECC4071` | levels/xp2_palace/squaddeathmatch | levels/xp2_palace/xp2_palace |
| `TeamDeathMatch.txt` | `4DB4204D-6EA2-42E1-A551-B1ED9C76971D` | `E4F4945F-F93D-C163-5892-3C7C3D0801B9` | levels/xp2_palace/teamdeathmatch | levels/xp2_palace/xp2_palace |
| `XP2_Palace.txt` | `BDCCA178-3187-41E6-BC8F-945FDC1B5E4C` | `BB7983EA-D791-3B54-B249-529D735C1D26` | levels/xp2_palace/xp2_palace | levels/xp2_palace/xp2_palace |

## XP2_Skybar（6 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `DOMINATION.txt` | `55BC5B5B-6039-4DDF-B273-2AEA13622E4B` | `1B42E26B-ECF3-9013-05E3-7F1B4A4B82CA` | levels/xp2_skybar/domination | levels/xp2_skybar/xp2_skybar |
| `DeathMatch.txt` | `F2B8C98F-F166-48CA-A63C-E7235DBF243F` | `1C820A38-4F85-14C2-3909-8C1921CDEC45` | levels/xp2_skybar/deathmatch | levels/xp2_skybar/xp2_skybar |
| `GunMaster.txt` | `06B999B3-6989-46C3-BCF3-37DEC0B7A531` | `412E7620-8C4D-A090-AFF0-37057687F097` | levels/xp2_skybar/gunmaster | levels/xp2_skybar/xp2_skybar |
| `SquadDM.txt` | `2A7C889E-3ABE-4906-9241-3C0EC21723FD` | `D437D8AF-D926-7FFB-3F23-4702706408F1` | levels/xp2_skybar/squaddm | levels/xp2_skybar/xp2_skybar |
| `TeamDM.txt` | `9C2135CC-2330-4FBA-9ED7-E08620FE4093` | `400F1AEF-770E-8D67-1CC4-DA11D85AE58E` | levels/xp2_skybar/teamdm | levels/xp2_skybar/xp2_skybar |
| `XP2_Skybar.txt` | `2DF41167-0BAB-11E1-AA4E-EFBA5D767A10` | `96EF016C-4246-27BF-E65F-D93E823EA96C` | levels/xp2_skybar/xp2_skybar | levels/xp2_skybar/xp2_skybar |

## XP3_Alborz（11 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `CONQUEST.txt` | `523C8C98-5035-447E-8C85-2F06C56013C8` | `DB2AA8AA-7321-2425-28C9-C3AF1DDDD3D8` | levels/xp3_alborz/conquest | levels/xp3_alborz/xp3_alborz |
| `ConquestLarge01.txt` ★ | `3D4CEA4D-3B86-4253-9841-3257927FAB53` | `133F6403-333F-27C6-7C68-19BB4CA87882` | levels/xp3_alborz/conquestlarge01 | levels/xp3_alborz/xp3_alborz |
| `ConquestSmall01.txt` | `B03175AD-05CC-4E84-8723-2A11A3243D92` | `650F6349-D8B2-7C49-0524-98A954893AF9` | levels/xp3_alborz/conquestsmall01 | levels/xp3_alborz/xp3_alborz |
| `DEATHMATCH.txt` | `2D5F0E6A-4019-4F73-A416-E55CF5EE1A18` | `7DAC9E3D-BD82-7B26-3F32-985C7B40BD5C` | levels/xp3_alborz/deathmatch | levels/xp3_alborz/xp3_alborz |
| `RUSH.txt` | `51DFBED6-BFAA-4B01-BFDA-CDB6ABA1E0C4` | `EC91AB3B-B50F-CCE1-A1A3-0ABFBAC627D4` | levels/xp3_alborz/rush | levels/xp3_alborz/xp3_alborz |
| `RushLarge0.txt` ★ | `26997AC4-F3C5-42CF-BBC6-CEC65C881911` | `6C72B9D2-484E-A4D0-94FA-8A8D39357040` | levels/xp3_alborz/rushlarge0 | levels/xp3_alborz/xp3_alborz |
| `SQDM.txt` | `997B2826-566C-4B0E-BC5C-E87285322FD1` | `F6C4D4D4-7E11-1762-D664-08A44AEC7703` | levels/xp3_alborz/sqdm | levels/xp3_alborz/xp3_alborz |
| `SquadRush0.txt` | `B8C7A953-31D6-4D7A-B3DF-8C8310C34EC3` | `4B2342C5-2A73-9D7E-A44B-74BFB63758FB` | levels/xp3_alborz/squadrush0 | levels/xp3_alborz/xp3_alborz |
| `TDM.txt` | `62B6664A-E2A2-43C7-8904-80420025FE5B` | `46220BCE-B44A-C5C2-8B49-EA1B2BDE011D` | levels/xp3_alborz/tdm | levels/xp3_alborz/xp3_alborz |
| `TankSuperiority.txt` | `2B7BF028-1092-4F4A-884B-5FE3CF28979C` | `CD70A930-51EA-10C5-9452-C0E340A8AA32` | levels/xp3_alborz/tanksuperiority | levels/xp3_alborz/xp3_alborz |
| `XP3_Alborz.txt` | `707F4A91-B837-47AC-8BEE-5EB614399714` | `4E0D56D9-0A2C-0C32-E2CA-DD032F4EBFE9` | levels/xp3_alborz/xp3_alborz | levels/xp3_alborz/xp3_alborz |

## XP3_Desert（11 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `CONQUEST.txt` | `5BC8BB57-D053-42EE-8F6B-AC74FC49E914` | `6FB4DB07-F1EB-F5D5-DE71-EA3965D129E4` | levels/xp3_desert/conquest | levels/xp3_desert/xp3_desert |
| `ConquestLarge0.txt` | `FD899CDE-78E2-409A-8FFE-68828370D627` | `4F81CD2D-1683-F9EE-304D-91260ACB625C` | levels/xp3_desert/conquestlarge0 | levels/xp3_desert/xp3_desert |
| `ConquestSmall0.txt` | `82984037-62DE-48C2-94F1-D58E95933097` | `D2C49805-C8D6-648A-4FE2-1C27240320F1` | levels/xp3_desert/conquestsmall0 | levels/xp3_desert/xp3_desert |
| `DEATHMATCH.txt` | `E17F2BE4-B0D5-4E23-B2A9-BAF6DB130E2E` | `DF639B25-46A9-604E-DCAF-21C418DFC413` | levels/xp3_desert/deathmatch | levels/xp3_desert/xp3_desert |
| `RUSH.txt` | `FEE621E0-824E-4EA2-8A17-51B268623BAD` | `FC24B055-67C6-42D9-9F34-831EF2DCC4A4` | levels/xp3_desert/rush | levels/xp3_desert/xp3_desert |
| `RushLarge0.txt` | `84E193AC-B7A6-4912-A8A4-D8E2544F9778` | `724E2BD4-CFEB-0C82-3A11-8FC98EFB765E` | levels/xp3_desert/rushlarge0 | levels/xp3_desert/xp3_desert |
| `SquadDeathMatch1.txt` | `83B14FF4-F2E7-4958-B0BE-4A70E3AEE2FB` | `12B51009-219C-E31F-D781-0B4B963321FD` | levels/xp3_desert/squaddeathmatch1 | levels/xp3_desert/xp3_desert |
| `SquadRush0.txt` | `8C81BA4B-EC59-4D7A-A14D-8FC9FA692A98` | `4BF9F070-9789-320C-E7C5-9BCAB33C9CF9` | levels/xp3_desert/squadrush0 | levels/xp3_desert/xp3_desert |
| `TANKSUPERIORITY.txt` | `6B832974-D17B-4F44-87D7-65EDC987BB7E` | `A57D1945-E33C-25B8-1B1D-D3E2519C64DF` | levels/xp3_desert/tanksuperiority | levels/xp3_desert/xp3_desert |
| `TeamDeathMatch1.txt` | `4486A842-F777-4832-966C-232C37BAF5DD` | `C7218193-E748-874C-1A4A-3B9D9F2F066F` | levels/xp3_desert/teamdeathmatch1 | levels/xp3_desert/xp3_desert |
| `XP3_Desert.txt` | `4CA1C116-7FA3-4163-A17E-325ACD02FD4F` | `273AC4A3-21D1-3D7E-B740-9387A30E1AF7` | levels/xp3_desert/xp3_desert | levels/xp3_desert/xp3_desert |

## XP3_Shield（11 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `CONQUEST.txt` | `94DD4853-9F33-4AAB-8277-71E5DE49EF33` | `B8E79336-A54A-0106-2078-BADB07ACB0F7` | levels/xp3_shield/conquest | levels/xp3_shield/xp3_shield |
| `ConquestLarge0.txt` | `40D68BE6-1CE4-436B-BC42-0DBD5C8DAA69` | `FC90635F-4589-EBB6-A323-EBB0050BC5BD` | levels/xp3_shield/conquestlarge0 | levels/xp3_shield/xp3_shield |
| `ConquestSmall0.txt` | `7A1FA42E-BF67-4412-A0FA-64AADA3166FA` | `336CEB6A-E4C0-DB68-3A96-883F6A239F7F` | levels/xp3_shield/conquestsmall0 | levels/xp3_shield/xp3_shield |
| `DEATHMATCH.txt` | `7B131650-78CC-4075-8480-A07876DCD36B` | `57E16046-023D-C1A6-B690-DAE8ACFA6D79` | levels/xp3_shield/deathmatch | levels/xp3_shield/xp3_shield |
| `RUSH.txt` | `2CBCF614-53FB-4617-B3FC-4E67CE54B32E` | `07D37E6A-24A9-6E89-B9FD-B0C5F01721C7` | levels/xp3_shield/rush | levels/xp3_shield/xp3_shield |
| `RushLarge.txt` | `CCE6FE0B-7C3A-4B6E-86CF-964F43D70136` | `ECACEAA3-6C5C-2FD0-7882-0FDCA03E81E2` | levels/xp3_shield/rushlarge | levels/xp3_shield/xp3_shield |
| `SQDM.txt` | `106FCB03-4FD7-4946-858B-2FEA666BD1D6` | `8B0D05BF-D0C7-FD1F-6360-A1890F109F51` | levels/xp3_shield/sqdm | levels/xp3_shield/xp3_shield |
| `SquadRush.txt` | `0FF6F420-60D2-4FAE-A3B3-B689BB00795A` | `BC3C1916-D790-F601-6041-9A36EF459D00` | levels/xp3_shield/squadrush | levels/xp3_shield/xp3_shield |
| `TDM.txt` | `B784E1CF-0C1D-43FF-AF9D-13A9D2C9B7DD` | `2622CA3F-001C-E396-EE22-867D22D63EC0` | levels/xp3_shield/tdm | levels/xp3_shield/xp3_shield |
| `TankSuperiority.txt` | `79458D28-E45E-4994-A7EB-65D2048CC0FD` | `EC7070D0-D37D-1022-FF1A-1C42CBBAEE72` | levels/xp3_shield/tanksuperiority | levels/xp3_shield/xp3_shield |
| `XP3_Shield.txt` | `69AFE35D-259F-11E1-98E7-C42BEF8FFB67` | `4396E861-4042-A682-5CD8-B00184DFECA1` | levels/xp3_shield/xp3_shield | levels/xp3_shield/xp3_shield |

## XP3_Valley（10 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `CQL0.txt` | `23E84714-2EC7-4ED4-90ED-DA7932BE548F` | `3F9320DB-1227-B55A-FAA6-57F77B478E68` | levels/xp3_valley/cql0 | levels/xp3_valley/xp3_valley |
| `CQS0.txt` | `4A33F98D-9C64-43E6-8756-2BE7F756555E` | `09B35C35-4DE9-2424-A6BD-784D4AE1DFF3` | levels/xp3_valley/cqs0 | levels/xp3_valley/xp3_valley |
| `Conquest.txt` | `38C542FB-CCFE-499A-A412-3DC1D7D319E4` | `86FE0381-17BF-50B0-2668-294B5301D33B` | levels/xp3_valley/conquest | levels/xp3_valley/xp3_valley |
| `DeathMatch.txt` | `B398436A-2C7E-4891-A975-7A9F76502CCF` | `63EB88C7-3B16-525B-577B-9CCA8C1159F4` | levels/xp3_valley/deathmatch | levels/xp3_valley/xp3_valley |
| `Rush.txt` | `446E3B83-7F86-4C84-9ACD-750C14E3E0D7` | `391A83D0-BC91-C5B6-73BC-6FA1C8C08B53` | levels/xp3_valley/rush | levels/xp3_valley/xp3_valley |
| `SQDM.txt` | `DE04DF0C-DDBC-47EB-8D59-9129A8CD7400` | `E921E14D-0C2F-A795-656A-DDD45E61EAF4` | levels/xp3_valley/sqdm | levels/xp3_valley/xp3_valley |
| `SquadRush.txt` | `E42AD3CE-C2AD-4192-A7F6-C8264E389EBB` | `0A0BE91A-EB7F-7A79-9C40-7131E16FD398` | levels/xp3_valley/squadrush | levels/xp3_valley/xp3_valley |
| `TDM.txt` | `7BCFD6D1-517D-4EE0-B78F-F9C9CF5AFC4E` | `ADBE1A66-C645-86A8-B939-62C471AE13CC` | levels/xp3_valley/tdm | levels/xp3_valley/xp3_valley |
| `TankSuperiority.txt` | `2CC7D28B-DEEA-409D-AA3D-1B97F1C01A8A` | `371C6ECE-EC6F-D214-216C-41E00CEC04F6` | levels/xp3_valley/tanksuperiority | levels/xp3_valley/xp3_valley |
| `XP3_Valley.txt` | `B72E95FE-1681-11E1-8C62-84EAE0530135` | `6E2FB064-22B2-3599-F448-B1B9A0B782AE` | levels/xp3_valley/xp3_valley | levels/xp3_valley/xp3_valley |

## XP4_FD（12 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Conquest.txt` | `2F464005-799D-4952-B6E3-C7888A2BFAEB` | `0E2B4989-1CB1-D84E-7A16-E31B217FA2A2` | levels/xp4_fd/conquest | levels/xp4_fd/xp4_fd |
| `Conquest_Large.txt` | `838247BA-E50C-4AFE-9651-AF488AD96F8D` | `5BCFD1AB-1F1B-6050-8BAE-B53A243BB1A9` | levels/xp4_fd/conquest_large | levels/xp4_fd/xp4_fd |
| `Conquest_Small0.txt` | `543C3C9B-C159-4749-8DE4-3DA1EAD12D5F` | `AA66B62E-07F1-E003-4721-13E50A1B7A3A` | levels/xp4_fd/conquest_small0 | levels/xp4_fd/xp4_fd |
| `DeathMatch.txt` | `7F40042E-0630-4777-BFC2-19853DA6E333` | `E862815B-761B-8161-2B2B-CD0A50D3EFE5` | levels/xp4_fd/deathmatch | levels/xp4_fd/xp4_fd |
| `GunMaster.txt` | `C0B44785-E88F-4D70-B1D1-4CBBB9E1FB2D` | `B04BE93A-65B7-9F96-3251-B589E6762840` | levels/xp4_fd/gunmaster | levels/xp4_fd/xp4_fd |
| `Rush.txt` | `9D68C8EE-064E-4090-8F97-A87DAE50D94B` | `22AB66CB-28EF-FCA5-01A6-2E5A8A9FD5F7` | levels/xp4_fd/rush | levels/xp4_fd/xp4_fd |
| `Rushes.txt` | `9D90DFFB-B053-445B-9FA5-2DF72725B52B` | `A0B353C5-E51D-7457-13B5-6F34FE8ECD03` | levels/xp4_fd/rushes | levels/xp4_fd/xp4_fd |
| `Scavenger_V2.txt` | `C83DAF64-4FAC-4398-8501-7D80BC9596E8` | `8B4E0F6C-A504-3404-C586-2DC6BD41A781` | levels/xp4_fd/scavenger_v2 | levels/xp4_fd/xp4_fd |
| `SquadDeathMatch.txt` | `07FB04CD-CD96-443D-8EAC-35AABC7E811B` | `79B024C5-C8F6-F109-1B9C-2F805C655447` | levels/xp4_fd/squaddeathmatch | levels/xp4_fd/xp4_fd |
| `SquadRush.txt` | `278BD270-16AB-4E4C-B11C-46615B5B5E32` | `C83ABCDC-748B-B051-9C26-B31A8CAF9A93` | levels/xp4_fd/squadrush | levels/xp4_fd/xp4_fd |
| `TeamDeathMatch.txt` | `9D1E1BF6-0188-45F4-B795-96BDC65651F0` | `B648D67F-6966-BD35-5DC7-A1854ABEEAAC` | levels/xp4_fd/teamdeathmatch | levels/xp4_fd/xp4_fd |
| `XP4_FD.txt` | `E1190F63-3B98-11E1-9705-98D5EF3C46D1` | `0DE2A2B5-7709-BE2D-3555-154943286FD6` | levels/xp4_fd/xp4_fd | levels/xp4_fd/xp4_fd |

## XP4_Parl（12 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Conquest.txt` | `A8BBA5CC-B22B-41E9-9C13-A784F9D30DBD` | `B8752E3D-4C53-45C8-C2E1-4FDDD9D7ED9E` | levels/xp4_parl/conquest | levels/xp4_parl/xp4_parl |
| `Conquest_Large.txt` | `DD4439C2-3322-41A7-BD64-B6861F23E298` | `03335168-3C84-6F20-4BC0-275023C9C6BB` | levels/xp4_parl/conquest_large | levels/xp4_parl/xp4_parl |
| `Conquest_Small.txt` | `CB8490B6-C6B5-43A3-A6A6-CF2296D4AB9F` | `CF8760B8-0DF2-17D6-C08F-D5709D59E968` | levels/xp4_parl/conquest_small | levels/xp4_parl/xp4_parl |
| `DeathMatch.txt` | `ED562C6C-34D5-4626-8665-09B3BACFEE83` | `AD0C5F0C-D549-438C-8312-668D22886158` | levels/xp4_parl/deathmatch | levels/xp4_parl/xp4_parl |
| `GunMaster.txt` | `E60B498C-D298-447E-B2CA-A3B35687F662` | `A33054F1-B03B-007F-1794-85A81608E001` | levels/xp4_parl/gunmaster | levels/xp4_parl/xp4_parl |
| `Rush.txt` | `4108B600-81F7-4531-8C43-9F755EF98063` | `B17E1E5D-43AF-05E6-11C2-C74772635072` | levels/xp4_parl/rush | levels/xp4_parl/xp4_parl |
| `Rushlarge.txt` | `064036DA-AAD2-4ED4-8D24-3FB1A9A15942` | `534BC70D-6C78-CBD5-B702-CECB813A5014` | levels/xp4_parl/rushlarge | levels/xp4_parl/xp4_parl |
| `Scavenger.txt` | `60D0C211-6FE2-4BC8-B28E-9D251F24E561` | `C6AC1C44-4689-FDCB-4EED-692974D189A8` | levels/xp4_parl/scavenger | levels/xp4_parl/xp4_parl |
| `SquadDeathMatch.txt` | `797C02B9-E9F2-4819-9B3C-E8B4A73FF6C0` | `87E4C059-5D7A-AB62-2D7F-00A5BDE316FB` | levels/xp4_parl/squaddeathmatch | levels/xp4_parl/xp4_parl |
| `SquadRush.txt` | `E698D6AC-2D01-4007-815F-28D3DDE36C1C` | `7AB9D9CE-924D-9162-6AB1-F593D1CEE8BA` | levels/xp4_parl/squadrush | levels/xp4_parl/xp4_parl |
| `TeamDeathMatch.txt` | `A2D92A00-7301-48A5-8431-B6B8C595476C` | `512B68E5-D0D3-E2F0-60CA-981CE79A451C` | levels/xp4_parl/teamdeathmatch | levels/xp4_parl/xp4_parl |
| `XP4_Parl.txt` | `8AB5A886-48D5-11E1-9377-EB75ECF8D98B` | `9DEBB2BF-66A4-9A1F-64A0-792952F93DBF` | levels/xp4_parl/xp4_parl | levels/xp4_parl/xp4_parl |

## XP4_Quake（12 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Conquest.txt` | `A2116B41-2B5C-4D8D-B932-8B7F02999F65` | `8A79769E-838E-33ED-D804-D3856CAEE81A` | levels/xp4_quake/conquest | levels/xp4_quake/xp4_quake |
| `Conquest_Large.txt` | `A1754860-6A22-4C57-851F-457A12E76FC0` | `E1F98AB8-37A6-F432-C954-1C0CCFA9B457` | levels/xp4_quake/conquest_large | levels/xp4_quake/xp4_quake |
| `Conquest_Small.txt` | `E4B3C39B-3A4B-425E-8B73-F899AD0B9620` | `61AE1F7B-5BFA-A4C0-E36D-C4D8798EA8B4` | levels/xp4_quake/conquest_small | levels/xp4_quake/xp4_quake |
| `DeathMatch.txt` | `1FB76ACB-24E9-4FB6-93AC-CA4AA6C24C70` | `599D6EB1-CCE3-7B94-0CC0-1660D051F186` | levels/xp4_quake/deathmatch | levels/xp4_quake/xp4_quake |
| `GunMaster.txt` | `B196BC35-EAF2-4961-9DC2-8B462BE9626C` | `FF2CE48C-F5A4-2BCC-B0BA-0D615AF34B1F` | levels/xp4_quake/gunmaster | levels/xp4_quake/xp4_quake |
| `RushLarge.txt` | `198013C7-442C-4134-8117-907EAE616620` | `146067E0-645D-673F-7F82-576D62C58C34` | levels/xp4_quake/rushlarge | levels/xp4_quake/xp4_quake |
| `Rushes.txt` | `79FAC3AF-D687-4CC8-A4E2-866758452EA6` | `E50F6653-0110-2A72-ABA4-9FA23EAE7F45` | levels/xp4_quake/rushes | levels/xp4_quake/xp4_quake |
| `Scavenger.txt` | `8E4F1A77-797A-4398-9CC6-65FB3AFFF9CC` | `9F6C3EE6-8A2B-DD19-259A-16E0D344BEAB` | levels/xp4_quake/scavenger | levels/xp4_quake/xp4_quake |
| `SquadDeathMatch.txt` | `FF849359-D9A5-43BB-B156-599AF1A358E8` | `07FE0D79-AAD9-D245-880B-4E82E84E3AFD` | levels/xp4_quake/squaddeathmatch | levels/xp4_quake/xp4_quake |
| `SquadRush.txt` | `30F03F12-47F7-4CAE-8262-5E38D2C23641` | `E67396CF-A7B3-AE73-398C-4DFBB739A213` | levels/xp4_quake/squadrush | levels/xp4_quake/xp4_quake |
| `TeamDeathMatch.txt` | `EE148C46-5A4A-455C-9D06-EB1F80C8E2C0` | `65F486AB-B1DB-DF28-79B1-5176B00DC9E2` | levels/xp4_quake/teamdeathmatch | levels/xp4_quake/xp4_quake |
| `XP4_Quake.txt` | `08A6147C-5992-11E1-A747-C08769BF799B` | `3DF7642C-B33F-8CCD-344A-FC252B169109` | levels/xp4_quake/xp4_quake | levels/xp4_quake/xp4_quake |

## XP4_Rubble（12 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Conquest.txt` | `F1C1416B-7C6A-40D9-A595-A05D30709526` | `EA0E14CD-4BAF-B8D4-0F4C-CAC56F6C2493` | levels/xp4_rubble/conquest | levels/xp4_rubble/xp4_rubble |
| `Conquest_Large.txt` | `E93C3B2B-4A1C-4A6F-A44E-B057569E883F` | `3527EAD8-C310-63B1-024F-522EF3BACBA0` | levels/xp4_rubble/conquest_large | levels/xp4_rubble/xp4_rubble |
| `Conquest_Small.txt` | `A2ABC550-B900-441F-8030-7CC3E18BB2BC` | `D4D1303B-0B58-C4BC-BC06-5D3121810E1D` | levels/xp4_rubble/conquest_small | levels/xp4_rubble/xp4_rubble |
| `DeatMatch.txt` | `B431C1A9-FEC1-4D46-9A7D-FF77C28C33E7` | `CCDC5043-4B14-B580-B74F-05725D1CD07C` | levels/xp4_rubble/deatmatch | levels/xp4_rubble/xp4_rubble |
| `GunMaster.txt` | `947397E3-5407-4174-9CBF-1757A95385C1` | `54B85709-67A0-8B81-8695-B78896E1DF55` | levels/xp4_rubble/gunmaster | levels/xp4_rubble/xp4_rubble |
| `Rush_Large.txt` | `35FA771D-D1E4-44E8-B28D-2DB5D487EB68` | `FC064268-7B88-D7F5-53DA-73A0C57CBA1A` | levels/xp4_rubble/rush_large | levels/xp4_rubble/xp4_rubble |
| `Rushes.txt` | `66B2086D-284A-49F7-975F-122BA933A69A` | `F2FA8D06-9264-3253-72CB-85E25D98D36C` | levels/xp4_rubble/rushes | levels/xp4_rubble/xp4_rubble |
| `Scavenger.txt` | `31994A36-F0E5-43B1-BF50-11A96C7035E8` | `0C090C4C-1C4E-580F-EA70-4F8EEC194B34` | levels/xp4_rubble/scavenger | levels/xp4_rubble/xp4_rubble |
| `SquadDeathMatch.txt` | `119BB2BF-E087-463F-B789-A09C89D6B81E` | `B8656C14-D85C-282B-D807-43543F700CEB` | levels/xp4_rubble/squaddeathmatch | levels/xp4_rubble/xp4_rubble |
| `Squad_Rush.txt` | `BE2338C9-999C-4F45-B3A5-AADBB32F79F4` | `181755E6-4A7D-A2C3-E8D0-4E253ED6811C` | levels/xp4_rubble/squad_rush | levels/xp4_rubble/xp4_rubble |
| `TeamDeathMatch.txt` | `C835082C-86EE-4586-A13A-0CCF1334DFFD` | `7006F101-6CD4-93F4-A518-D014C61C601A` | levels/xp4_rubble/teamdeathmatch | levels/xp4_rubble/xp4_rubble |
| `XP4_Rubble.txt` | `6FEEBB6D-9B66-11E1-847F-A3C20EE63DF4` | `8CE9839B-69A5-8468-369B-9BD4A003A0F3` | levels/xp4_rubble/xp4_rubble | levels/xp4_rubble/xp4_rubble |

## XP5_001（11 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Air_Superiority.txt` | `558AD19C-6FB6-4497-98C4-E434E71CEE76` | `4EE4D634-E451-F395-AFCE-756319ABEA33` | levels/xp5_001/air_superiority | levels/xp5_001/xp5_001 |
| `CQL.txt` | `25BBF5C7-2AD0-4C4C-9AF3-57CCD9CAB017` | `45977445-06C0-0441-4C91-90E41D64ECE2` | levels/xp5_001/cql | levels/xp5_001/xp5_001 |
| `CQS.txt` | `997A0F24-FE72-419F-8A45-64B924285FD2` | `01BF1CBE-BC2B-2C26-BBCC-7E0DD53B2BA9` | levels/xp5_001/cqs | levels/xp5_001/xp5_001 |
| `CTF.txt` | `3345CA4E-D64D-40C8-827F-B8F67AEDB7CE` | `0A26AECC-CDB9-0311-D08A-E1529F4CFD60` | levels/xp5_001/ctf | levels/xp5_001/xp5_001 |
| `Conquest.txt` | `A1670523-D80D-482F-A93D-6CF48819F896` | `B62FFD23-8E9A-3491-913C-5C65C430C71C` | levels/xp5_001/conquest | levels/xp5_001/xp5_001 |
| `DM.txt` | `E9BD9203-851A-46CF-B811-1DFEAE398145` | `7ECA71AC-E1D5-D7C3-A522-8C54B07150DD` | levels/xp5_001/dm | levels/xp5_001/xp5_001 |
| `Rush.txt` | `7241927C-26E0-44E8-848B-B4509E7DF3BA` | `FB03C297-1B49-D1E5-2C22-DB6D1FC5A3F4` | levels/xp5_001/rush | levels/xp5_001/xp5_001 |
| `SQDM.txt` | `86714079-8B5F-45D7-AB9F-08BBBA3814BC` | `DAF72AEC-7601-1890-7680-B582E09BC225` | levels/xp5_001/sqdm | levels/xp5_001/xp5_001 |
| `SquadRush.txt` | `9C122648-C2B6-486C-B9EF-E1BF173D73D6` | `FCB0C8A5-5129-02BE-69E8-2F5A3EB70121` | levels/xp5_001/squadrush | levels/xp5_001/xp5_001 |
| `TDM.txt` | `92B3AF2B-F118-43C4-8002-D466335A9B23` | `DDA0F10F-CB40-E042-8457-D197C46F18BA` | levels/xp5_001/tdm | levels/xp5_001/xp5_001 |
| `XP5_001.txt` | `3DF41561-D87B-4526-B153-85D09BAA07C7` | `A41B961E-6150-F294-6A67-E307D1E30B2E` | levels/xp5_001/xp5_001 | levels/xp5_001/xp5_001 |

## XP5_002（11 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `Air_Superiority.txt` | `B97E8E65-574E-4480-AE61-3CFAC4C86D73` | `89EFDC23-5A0B-4F2D-0280-EC390E593CF3` | levels/xp5_002/air_superiority | levels/xp5_002/xp5_002 |
| `CQL.txt` | `EDBFB91A-F8EA-492D-A5FA-39D6AC2DC525` | `421454A2-6F76-B4C6-7240-322C71D8DDAB` | levels/xp5_002/cql | levels/xp5_002/xp5_002 |
| `CQS.txt` | `CF38A24C-D379-4830-BA78-81968A4F786F` | `08630B66-BC5A-FA5F-93F7-273CF90D4B91` | levels/xp5_002/cqs | levels/xp5_002/xp5_002 |
| `CTF.txt` | `65002E2F-1D1D-429A-B517-541D2CDD90A6` | `16D9C40E-68AA-3149-27C5-99693209409B` | levels/xp5_002/ctf | levels/xp5_002/xp5_002 |
| `Conquest.txt` | `B7455D2B-E411-47C4-BB9F-A89C6AE74D04` | `358426EB-CC24-9806-7A71-6F8ACB9EC411` | levels/xp5_002/conquest | levels/xp5_002/xp5_002 |
| `DM.txt` | `3AFAB808-F90A-492F-9659-B9DB8E9C7BA7` | `C381E96F-2F92-3693-441C-12EC11EFDFE9` | levels/xp5_002/dm | levels/xp5_002/xp5_002 |
| `Rush.txt` | `9FCC6B39-E554-4A8A-848E-69E241F27F41` | `EE09235D-AA6F-A2F6-7224-9E4D8885368D` | levels/xp5_002/rush | levels/xp5_002/xp5_002 |
| `SQDM.txt` | `67DCD4B7-537A-407B-8418-D6504FDED31D` | `EE5C71D3-49C8-2402-B293-BB597DB4C2FA` | levels/xp5_002/sqdm | levels/xp5_002/xp5_002 |
| `SquadRush.txt` | `A45DDE94-D012-45D6-975E-FF798447926D` | `4AE96648-5B17-780F-7A25-26E61010ACC3` | levels/xp5_002/squadrush | levels/xp5_002/xp5_002 |
| `TDM.txt` | `65413D06-8113-49B7-BC73-506CC3E34372` | `26EE02F8-6D57-D131-9E3C-96F2FAD97F71` | levels/xp5_002/tdm | levels/xp5_002/xp5_002 |
| `XP5_002.txt` | `C4A49551-19D4-11E2-A0B4-E3BFB6B30185` | `E1624182-AE5E-0EAE-2CF9-85249841840E` | levels/xp5_002/xp5_002 | levels/xp5_002/xp5_002 |

## XP5_003（11 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `AirSueriority.txt` | `8607997B-73D4-4C61-8194-82B178B35EAD` | `0306CBFA-CCD5-8A37-2B88-8FA193AB8F30` | levels/xp5_003/airsueriority | levels/xp5_003/xp5_003 |
| `CQL.txt` | `4D59552D-787F-402E-8FED-7B360186BD8A` | `D52CD0C7-7BFF-EDC8-1198-1CC70F9E68F8` | levels/xp5_003/cql | levels/xp5_003/xp5_003 |
| `CQS.txt` | `F7D5BBD2-6AD5-46B1-AC88-9E897CF1B81F` | `E17FD2F1-B85E-AA67-18FB-5FE0B535910A` | levels/xp5_003/cqs | levels/xp5_003/xp5_003 |
| `CTF.txt` | `5EAF9774-CAEE-4D88-BF81-108E0E043FCB` | `420697EB-CC4C-F5D3-E250-D2411F0C3877` | levels/xp5_003/ctf | levels/xp5_003/xp5_003 |
| `Conquest.txt` | `6C0D021C-80D8-4BDE-85F7-CDF6231F95D5` | `DE06D870-4193-F89F-0024-66337EC3F0AF` | levels/xp5_003/conquest | levels/xp5_003/xp5_003 |
| `DM.txt` | `DD29B28D-31AE-48A8-A781-ADECCA0D6A62` | `622BDB97-7B4C-13F2-31A4-4DAA3991093A` | levels/xp5_003/dm | levels/xp5_003/xp5_003 |
| `Rush.txt` | `7FC2EF94-48A0-44BF-A0A2-515E3DB2F276` | `1A76BA12-1A71-DC60-A79F-ED56BE814E29` | levels/xp5_003/rush | levels/xp5_003/xp5_003 |
| `SQDM.txt` | `AC196C72-63C4-4A3E-AB3B-BA91E3D3D38F` | `EFD0B517-A431-9434-B5B3-5908137AF8F8` | levels/xp5_003/sqdm | levels/xp5_003/xp5_003 |
| `SquadRush.txt` | `EF4988AF-975C-44D3-A605-B4E57239A7B6` | `85B91866-7E97-F265-1F0F-AC92846B8B6D` | levels/xp5_003/squadrush | levels/xp5_003/xp5_003 |
| `TDM.txt` | `084CF593-D6A5-42C0-A503-93373FA412D6` | `0B6C2A75-B0CD-2093-617B-E93E2B94BA92` | levels/xp5_003/tdm | levels/xp5_003/xp5_003 |
| `XP5_003.txt` | `CB9932E2-19E0-11E2-93EC-B0D4179CEA18` | `01006140-6949-3123-5412-649CE2814E2F` | levels/xp5_003/xp5_003 | levels/xp5_003/xp5_003 |

## XP5_004（11 个注册表）

| 模式分区 | ② 分区 GUID | ③ RegistryContainer GUID | ① bundle 名（LoadBundles 注入） | ④ superbundle（MountSuperBundle） |
|---|---|---|---|---|
| `AirSuperiority.txt` | `81021881-4B84-4F7A-BFE4-ADB7E6D4BEEE` | `B6238E2F-A7E5-2B20-C711-980E40C54147` | levels/xp5_004/airsuperiority | levels/xp5_004/xp5_004 |
| `CQL.txt` | `BF796B16-4BBD-4D46-BFDA-BC6568BAEAEA` | `C00FAE31-9E59-7C29-8216-BA2F7AAC4464` | levels/xp5_004/cql | levels/xp5_004/xp5_004 |
| `CQS.txt` | `39E344DB-BDF4-4991-A3CB-EAD69EDBE551` | `A724C894-E825-6AD8-2878-A057E2A497CC` | levels/xp5_004/cqs | levels/xp5_004/xp5_004 |
| `CTF.txt` | `4210A5DE-754B-4881-9C0E-E37EEF0542EF` | `DD65DCFF-51C7-9AD4-3F48-3D824CFF8178` | levels/xp5_004/ctf | levels/xp5_004/xp5_004 |
| `Conquest.txt` | `446013E9-768F-4038-B300-A0473785162F` | `BFC7C364-9A45-497A-95D8-32918E1F4F9A` | levels/xp5_004/conquest | levels/xp5_004/xp5_004 |
| `DM.txt` | `B1C0033B-E684-42E9-83DC-3304B867ECED` | `3DF18462-D672-B012-AA51-562F3AA8F3AC` | levels/xp5_004/dm | levels/xp5_004/xp5_004 |
| `Rush.txt` | `8A7CB0F3-D268-4669-8032-01BA94B5483A` | `15335144-67A1-D2BF-8EA1-E04206837082` | levels/xp5_004/rush | levels/xp5_004/xp5_004 |
| `SQDM.txt` | `50D882C3-ACA9-45BB-971B-5223374F3688` | `1B170434-18BF-9E2A-6702-254705DB62F0` | levels/xp5_004/sqdm | levels/xp5_004/xp5_004 |
| `SquadRush.txt` | `8EE1EAAF-A27C-469E-A6D9-414B8C98F1EB` | `AEEE5D46-24C2-0D90-CFA8-F90567D7C69A` | levels/xp5_004/squadrush | levels/xp5_004/xp5_004 |
| `TDM.txt` | `445E676C-BF09-4E7A-BC69-172DDB479918` | `45367098-B3D1-8A71-4101-B6C7B44340F9` | levels/xp5_004/tdm | levels/xp5_004/xp5_004 |
| `XP5_004.txt` | `07BE1949-19EA-11E2-8E8A-A9B21FEA266E` | `D08BA075-3DB4-B5CF-B0AF-425D1FE90234` | levels/xp5_004/xp5_004 | levels/xp5_004/xp5_004 |

## 没有注册表的 21 个目录（三分法，AddRegistry 在这些目录无锚点）

转储 70 个 Levels 目录里 21 个没有注册表，**不全是被砍图**（文件系统实测订正）：

| 类别 | 目录 | 对 bundles 工作流的含义 |
|---|---|---|
| 真被砍/未完成多人图（4） | MP_Canyon（248 分区）、MP_WhitePeak（522）、MP_BandarDesert 原版版、MP_019 | 有大量分区但无主分区/无注册表——AddRegistry 无锚点，注入需另找锚 |
| 资料片资产壳（4） | XP3_LeGrandVal（498）、XP4_Earthquake（511）、XP4_FinancialDistrict（385）、XP4_Parliament（354） | **不是图**：出货图 XP4_FD/XP4_Parl/XP4_Quake/XP4_Rubble 的资产库，关卡本体在本表 49 图内 |
| 测试图与桩（13） | Testrange×7、COOP_001/005/008、Shared、SP_003、SP_Interrogation | 测试/桩目录，无注入价值 |

完整定性见 FINDINGS.md #2。

## 附录 B：每图全量 bundle 清单（自官方 bundles.md）

> 用途：LoadBundles 注入选包 / 判断某包拉起什么。命名解码：`_parent`=区域逻辑层、
> `_art_parent`=美术层、`_gameconfiglight`=轻量配置、`_settings_win32`=图设置、`_ui*`=菜单流程包。

**COOP_002**（superbundle `levels/coop_002/coop_002`，18 个 bundle）

`levels/coop_002/ab01_art_parent`、`levels/coop_002/ab01_parent`、`levels/coop_002/ab02_art_parent`、`levels/coop_002/ab02_parent`、`levels/coop_002/ab03_art_parent`、`levels/coop_002/ab03_parent`、`levels/coop_002/ab04_art_parent`、`levels/coop_002/coop_002`、`levels/coop_002/coop_002_gameconfiglight_win32`、`levels/coop_002/coop_002_loading_music`、`levels/coop_002/coop_002_settings_win32`、`levels/coop_002/coop_002_uiendofround`、`levels/coop_002/coop_002_uiloadingmp`、`levels/coop_002/coop_002_uiloadingsp`、`levels/coop_002/coop_002_uiplaying`、`levels/coop_002/coop_002_uipreendofround`、`levels/coop_002/general_sluice_ab02_parent`、`levels/coop_002/general_sluice_ab03_parent`

**COOP_003**（superbundle `levels/coop_003/coop_003`，18 个 bundle）

`levels/coop_003/ab00_art_parent`、`levels/coop_003/ab00_art_sewer_parent`、`levels/coop_003/ab00_parent`、`levels/coop_003/ab00_sewer_parent`、`levels/coop_003/ab01_art_parent`、`levels/coop_003/ab01_parent`、`levels/coop_003/ab02_art_parent`、`levels/coop_003/ab02_parent`、`levels/coop_003/ab03_parent`、`levels/coop_003/coop_003`、`levels/coop_003/coop_003_gameconfiglight_win32`、`levels/coop_003/coop_003_loading_music`、`levels/coop_003/coop_003_settings_win32`、`levels/coop_003/coop_003_uiendofround`、`levels/coop_003/coop_003_uiloadingmp`、`levels/coop_003/coop_003_uiloadingsp`、`levels/coop_003/coop_003_uiplaying`、`levels/coop_003/coop_003_uipreendofround`

**COOP_006**（superbundle `levels/coop_006/coop_006`，15 个 bundle）

`levels/coop_006/ab00_vehicle_mobileaa_parent`、`levels/coop_006/ab01_gameplaycovers_parent`、`levels/coop_006/ab01_mortarteam_parent`、`levels/coop_006/ab01_parent`、`levels/coop_006/ab02_parent`、`levels/coop_006/ab03_parent`、`levels/coop_006/coop_006`、`levels/coop_006/coop_006_gameconfiglight_win32`、`levels/coop_006/coop_006_loading_music`、`levels/coop_006/coop_006_settings_win32`、`levels/coop_006/coop_006_uiendofround`、`levels/coop_006/coop_006_uiloadingmp`、`levels/coop_006/coop_006_uiloadingsp`、`levels/coop_006/coop_006_uiplaying`、`levels/coop_006/coop_006_uipreendofround`

**COOP_007**（superbundle `levels/coop_007/coop_007`，15 个 bundle）

`levels/coop_007/ab00_parent`、`levels/coop_007/ab01_parent`、`levels/coop_007/ab02_parent`、`levels/coop_007/ab04_parent`、`levels/coop_007/ab05_parent`、`levels/coop_007/coop_007`、`levels/coop_007/coop_007_gameconfiglight_win32`、`levels/coop_007/coop_007_loading_music`、`levels/coop_007/coop_007_settings_win32`、`levels/coop_007/coop_007_uiendofround`、`levels/coop_007/coop_007_uiloadingmp`、`levels/coop_007/coop_007_uiloadingsp`、`levels/coop_007/coop_007_uiplaying`、`levels/coop_007/coop_007_uipreendofround`、`levels/coop_007/stadium_ambience`

**COOP_009**（superbundle `levels/coop_009/coop_009`，20 个 bundle）

`levels/coop_009/ab00_art_interior_parent`、`levels/coop_009/ab00_art_parent`、`levels/coop_009/ab00_parent`、`levels/coop_009/ab01_art_parent`、`levels/coop_009/ab01_parent`、`levels/coop_009/ab02_art_parent`、`levels/coop_009/ab02_parent`、`levels/coop_009/ab03_art_parent`、`levels/coop_009/ab03_parent`、`levels/coop_009/ab_art_road_1_parent`、`levels/coop_009/ab_art_road_2_parent`、`levels/coop_009/coop_009`、`levels/coop_009/coop_009_gameconfiglight_win32`、`levels/coop_009/coop_009_loading_music`、`levels/coop_009/coop_009_settings_win32`、`levels/coop_009/coop_009_uiendofround`、`levels/coop_009/coop_009_uiloadingmp`、`levels/coop_009/coop_009_uiloadingsp`、`levels/coop_009/coop_009_uiplaying`、`levels/coop_009/coop_009_uipreendofround`

**COOP_010**（superbundle `levels/coop_010/coop_010`，19 个 bundle）

`levels/coop_010/ab00_art_parent`、`levels/coop_010/ab00_parent`、`levels/coop_010/ab01_ab03_buffer_parent`、`levels/coop_010/ab01_art_parent`、`levels/coop_010/ab01_parent`、`levels/coop_010/ab03_ab04_buffer_parent`、`levels/coop_010/ab03_parent`、`levels/coop_010/ab04_parent`、`levels/coop_010/ab05_parent`、`levels/coop_010/ab06_parent`、`levels/coop_010/coop_010`、`levels/coop_010/coop_010_gameconfiglight_win32`、`levels/coop_010/coop_010_loading_music`、`levels/coop_010/coop_010_settings_win32`、`levels/coop_010/coop_010_uiendofround`、`levels/coop_010/coop_010_uiloadingmp`、`levels/coop_010/coop_010_uiloadingsp`、`levels/coop_010/coop_010_uiplaying`、`levels/coop_010/coop_010_uipreendofround`

**FrontEnd**（superbundle `levels/frontend/frontend`，8 个 bundle）

`levels/frontend/frontend`、`levels/frontend/frontend_gameconfiglight_win32`、`levels/frontend/frontend_settings_win32`、`levels/frontend/frontend_uiendofround`、`levels/frontend/frontend_uiloadingmp`、`levels/frontend/frontend_uiloadingsp`、`levels/frontend/frontend_uiplaying`、`levels/frontend/frontend_uipreendofround`

**MP_001**（superbundle `levels/mp_001/mp_001`，17 个 bundle）

`levels/mp_001/conquest`、`levels/mp_001/conquest_large`、`levels/mp_001/lightcasters`、`levels/mp_001/mp_001`、`levels/mp_001/mp_001_gameconfiglight_win32`、`levels/mp_001/mp_001_loading_music`、`levels/mp_001/mp_001_settings_win32`、`levels/mp_001/mp_001_uiendofround`、`levels/mp_001/mp_001_uiloadingmp`、`levels/mp_001/mp_001_uiloadingsp`、`levels/mp_001/mp_001_uiplaying`、`levels/mp_001/mp_001_uipreendofround`、`levels/mp_001/rush`、`levels/mp_001/squad_deathmatch`、`levels/mp_001/squad_rush`、`levels/mp_001/tdm1`、`levels/mp_001/team_deathmatch`

**MP_003**（superbundle `levels/mp_003/mp_003`，18 个 bundle）

`levels/mp_003/common`、`levels/mp_003/conquestlarge`、`levels/mp_003/conquestsmall`、`levels/mp_003/mp_003`、`levels/mp_003/mp_003_gameconfiglight_win32`、`levels/mp_003/mp_003_loading_music`、`levels/mp_003/mp_003_settings_win32`、`levels/mp_003/mp_003_uiendofround`、`levels/mp_003/mp_003_uiloadingmp`、`levels/mp_003/mp_003_uiloadingsp`、`levels/mp_003/mp_003_uiplaying`、`levels/mp_003/mp_003_uipreendofround`、`levels/mp_003/rush3`、`levels/mp_003/squaddeathmatch`、`levels/mp_003/squadrush`、`levels/mp_003/tdm1`、`levels/mp_003/tdm2`、`levels/mp_003/teamdeathmatch`

**MP_007**（superbundle `levels/mp_007/mp_007`，17 个 bundle）

`levels/mp_007/conquest_large`、`levels/mp_007/conquest_small`、`levels/mp_007/mp_007`、`levels/mp_007/mp_007_gameconfiglight_win32`、`levels/mp_007/mp_007_loading_music`、`levels/mp_007/mp_007_settings_win32`、`levels/mp_007/mp_007_uiendofround`、`levels/mp_007/mp_007_uiloadingmp`、`levels/mp_007/mp_007_uiloadingsp`、`levels/mp_007/mp_007_uiplaying`、`levels/mp_007/mp_007_uipreendofround`、`levels/mp_007/rush`、`levels/mp_007/selective_art`、`levels/mp_007/squaddeathmatch`、`levels/mp_007/squadrush`、`levels/mp_007/tdm1`、`levels/mp_007/teamdeathmatch`

**MP_011**（superbundle `levels/mp_011/mp_011`，17 个 bundle）

`levels/mp_011/artpcexclusive`、`levels/mp_011/conquest_large`、`levels/mp_011/conquest_small`、`levels/mp_011/mp_011`、`levels/mp_011/mp_011_gameconfiglight_win32`、`levels/mp_011/mp_011_loading_music`、`levels/mp_011/mp_011_settings_win32`、`levels/mp_011/mp_011_uiendofround`、`levels/mp_011/mp_011_uiloadingmp`、`levels/mp_011/mp_011_uiloadingsp`、`levels/mp_011/mp_011_uiplaying`、`levels/mp_011/mp_011_uipreendofround`、`levels/mp_011/rush`、`levels/mp_011/squaddeathmatch`、`levels/mp_011/squadrush`、`levels/mp_011/teamdeathmatch`、`levels/mp_011/teamdeathmatch_01`

**MP_012**（superbundle `levels/mp_012/mp_012`，18 个 bundle）

`levels/mp_012/conquest_large`、`levels/mp_012/conquest_small`、`levels/mp_012/mp_012`、`levels/mp_012/mp_012_gameconfiglight_win32`、`levels/mp_012/mp_012_loading_music`、`levels/mp_012/mp_012_settings_win32`、`levels/mp_012/mp_012_uiendofround`、`levels/mp_012/mp_012_uiloadingmp`、`levels/mp_012/mp_012_uiloadingsp`、`levels/mp_012/mp_012_uiplaying`、`levels/mp_012/mp_012_uipreendofround`、`levels/mp_012/rush`、`levels/mp_012/squaddeathmatch`、`levels/mp_012/squadrush`、`levels/mp_012/teamdeathmatch`、`levels/mp_012/tutorialmp`、`levels/mp_012/tutorialmp_sandbox`、`levels/mp_012/tutorialmp_shoothouse`

**MP_013**（superbundle `levels/mp_013/mp_013`，17 个 bundle）

`levels/mp_013/conquestlarge`、`levels/mp_013/conquestsmall`、`levels/mp_013/mp_013`、`levels/mp_013/mp_013_gameconfiglight_win32`、`levels/mp_013/mp_013_loading_music`、`levels/mp_013/mp_013_settings_win32`、`levels/mp_013/mp_013_uiendofround`、`levels/mp_013/mp_013_uiloadingmp`、`levels/mp_013/mp_013_uiloadingsp`、`levels/mp_013/mp_013_uiplaying`、`levels/mp_013/mp_013_uipreendofround`、`levels/mp_013/pc_only`、`levels/mp_013/rush`、`levels/mp_013/squaddeathmatch`、`levels/mp_013/squadrush`、`levels/mp_013/tdm1`、`levels/mp_013/teamdeathmatch`

**MP_017**（superbundle `levels/mp_017/mp_017`，15 个 bundle）

`levels/mp_017/cql`、`levels/mp_017/cqs`、`levels/mp_017/mp_017`、`levels/mp_017/mp_017_gameconfiglight_win32`、`levels/mp_017/mp_017_loading_music`、`levels/mp_017/mp_017_settings_win32`、`levels/mp_017/mp_017_uiendofround`、`levels/mp_017/mp_017_uiloadingmp`、`levels/mp_017/mp_017_uiloadingsp`、`levels/mp_017/mp_017_uiplaying`、`levels/mp_017/mp_017_uipreendofround`、`levels/mp_017/r`、`levels/mp_017/sdm`、`levels/mp_017/sr`、`levels/mp_017/tdm`

**MP_018**（superbundle `levels/mp_018/mp_018`，20 个 bundle）

`levels/mp_018/conquest`、`levels/mp_018/conquest_large`、`levels/mp_018/conquest_large2`、`levels/mp_018/conquest_small`、`levels/mp_018/conquest_small2`、`levels/mp_018/mp_018`、`levels/mp_018/mp_018_gameconfiglight_win32`、`levels/mp_018/mp_018_loading_music`、`levels/mp_018/mp_018_settings_win32`、`levels/mp_018/mp_018_uiendofround`、`levels/mp_018/mp_018_uiloadingmp`、`levels/mp_018/mp_018_uiloadingsp`、`levels/mp_018/mp_018_uiplaying`、`levels/mp_018/mp_018_uipreendofround`、`levels/mp_018/mp_global2`、`levels/mp_018/rush`、`levels/mp_018/squaddeathmatch`、`levels/mp_018/squadrush`、`levels/mp_018/tdm1`、`levels/mp_018/teamdeathmatch`

**MP_Subway**（superbundle `levels/mp_subway/mp_subway`，20 个 bundle）

`levels/mp_subway/common`、`levels/mp_subway/conquest_small`、`levels/mp_subway/gameplayobjects`、`levels/mp_subway/mp_subway`、`levels/mp_subway/mp_subway_gameconfiglight_win32`、`levels/mp_subway/mp_subway_loading_music`、`levels/mp_subway/mp_subway_settings_win32`、`levels/mp_subway/mp_subway_uiendofround`、`levels/mp_subway/mp_subway_uiloadingmp`、`levels/mp_subway/mp_subway_uiloadingsp`、`levels/mp_subway/mp_subway_uiplaying`、`levels/mp_subway/mp_subway_uipreendofround`、`levels/mp_subway/rush`、`levels/mp_subway/squaddeathmatch`、`levels/mp_subway/squadrush`、`levels/mp_subway/tdm1`、`levels/mp_subway/tdm2`、`levels/mp_subway/teamdeathmatch`、`levels/mp_subway/teams_large`、`levels/mp_subway/teams_small`

**SP_Bank**（superbundle `levels/sp_bank/sp_bank`，55 个 bundle）

`levels/sp_bank/assault_sub`、`levels/sp_bank/assaultcanalprops_sub`、`levels/sp_bank/backdrop`、`levels/sp_bank/backdrophighway_sub`、`levels/sp_bank/bank_sub`、`levels/sp_bank/bmd`、`levels/sp_bank/breach_sub`、`levels/sp_bank/bridge_sub`、`levels/sp_bank/convoy_art_sub`、`levels/sp_bank/convoy_start_sub`、`levels/sp_bank/convoy_sub`、`levels/sp_bank/highway_01_ambience_sub`、`levels/sp_bank/highway_01_sub`、`levels/sp_bank/highway_02_sub`、`levels/sp_bank/highway_03_ambience_sub`、`levels/sp_bank/highway_03_props`、`levels/sp_bank/highway_03_sub`、`levels/sp_bank/house_art_sub`、`levels/sp_bank/house_props_sub`、`levels/sp_bank/house_sub`、`levels/sp_bank/intro_sub`、`levels/sp_bank/lightmap_01`、`levels/sp_bank/lightmap_02`、`levels/sp_bank/lightmap_03`、`levels/sp_bank/lightmap_04`、`levels/sp_bank/marines`、`levels/sp_bank/marines2`、`levels/sp_bank/ministry_ambience_sub`、`levels/sp_bank/ministry_sub`、`levels/sp_bank/passage_cutscene`、`levels/sp_bank/passage_sub`、`levels/sp_bank/plaza`、`levels/sp_bank/plaza_interior_sub`、`levels/sp_bank/plazalightz_sub`、`levels/sp_bank/plazaprops_sub`、`levels/sp_bank/regroup`、`levels/sp_bank/ride_ambience_sub`、`levels/sp_bank/ride_sub`、`levels/sp_bank/sp_bank`、`levels/sp_bank/sp_bank_gameconfiglight_win32`、`levels/sp_bank/sp_bank_loading_music`、`levels/sp_bank/sp_bank_settings_win32`、`levels/sp_bank/sp_bank_uiendofround`、`levels/sp_bank/sp_bank_uiloadingmp`、`levels/sp_bank/sp_bank_uiloadingsp`、`levels/sp_bank/sp_bank_uiplaying`、`levels/sp_bank/sp_bank_uipreendofround`、`levels/sp_bank/tank_art_sub`、`levels/sp_bank/tank_sub`、`levels/sp_bank/trenchintro`、`levels/sp_bank/vault_sub`、`levels/sp_bank/vaultart_sub`、`levels/sp_bank/vaultdescentanimations`、`levels/sp_bank/vaultendanimations`、`levels/sp_bank/vaultstream_sub`

**SP_Earthquake**（superbundle `levels/sp_earthquake/sp_earthquake`，37 个 bundle）

`levels/sp_earthquake/alley`、`levels/sp_earthquake/backdrop`、`levels/sp_earthquake/bazaar`、`levels/sp_earthquake/bazaarfacade`、`levels/sp_earthquake/bridgefight`、`levels/sp_earthquake/briefing`、`levels/sp_earthquake/building`、`levels/sp_earthquake/cellar`、`levels/sp_earthquake/earthquake`、`levels/sp_earthquake/ied`、`levels/sp_earthquake/lavscene`、`levels/sp_earthquake/lavsceneoccluders`、`levels/sp_earthquake/lightmap_01`、`levels/sp_earthquake/lightmap_02`、`levels/sp_earthquake/lightmap_03`、`levels/sp_earthquake/meatmarket`、`levels/sp_earthquake/parkinglot`、`levels/sp_earthquake/parkinglotsurroundings`、`levels/sp_earthquake/rooftop`、`levels/sp_earthquake/rooftopextraction`、`levels/sp_earthquake/rooftopparkour`、`levels/sp_earthquake/rooftopsniper`、`levels/sp_earthquake/school`、`levels/sp_earthquake/schoolbuilding`、`levels/sp_earthquake/sp_earthquake`、`levels/sp_earthquake/sp_earthquake_gameconfiglight_win32`、`levels/sp_earthquake/sp_earthquake_loading_music`、`levels/sp_earthquake/sp_earthquake_settings_win32`、`levels/sp_earthquake/sp_earthquake_uiendofround`、`levels/sp_earthquake/sp_earthquake_uiloadingmp`、`levels/sp_earthquake/sp_earthquake_uiloadingsp`、`levels/sp_earthquake/sp_earthquake_uiplaying`、`levels/sp_earthquake/sp_earthquake_uipreendofround`、`levels/sp_earthquake/stagingarea`、`levels/sp_earthquake/stagingareasurroundings`、`levels/sp_earthquake/stagingareawin32`、`levels/sp_earthquake/streetcrossing`

**SP_Earthquake2**（superbundle `levels/sp_earthquake2/sp_earthquake2`，27 个 bundle）

`levels/sp_earthquake2/alley_sub`、`levels/sp_earthquake2/backdrop`、`levels/sp_earthquake2/bazaar_sub`、`levels/sp_earthquake2/cafe_doorsub`、`levels/sp_earthquake2/cafe_meetmontes`、`levels/sp_earthquake2/cafe_sub`、`levels/sp_earthquake2/largebuilding_sub`、`levels/sp_earthquake2/lightmap_01`、`levels/sp_earthquake2/lightmap_02`、`levels/sp_earthquake2/lightmap_03`、`levels/sp_earthquake2/meatmarket_sub`、`levels/sp_earthquake2/parkinglot_sub`、`levels/sp_earthquake2/rift2_sub`、`levels/sp_earthquake2/rift_sub`、`levels/sp_earthquake2/school_sub`、`levels/sp_earthquake2/solomon_intro`、`levels/sp_earthquake2/sp_earthquake2`、`levels/sp_earthquake2/sp_earthquake2_gameconfiglight_win32`、`levels/sp_earthquake2/sp_earthquake2_loading_music`、`levels/sp_earthquake2/sp_earthquake2_settings_win32`、`levels/sp_earthquake2/sp_earthquake2_uiendofround`、`levels/sp_earthquake2/sp_earthquake2_uiloadingmp`、`levels/sp_earthquake2/sp_earthquake2_uiloadingsp`、`levels/sp_earthquake2/sp_earthquake2_uiplaying`、`levels/sp_earthquake2/sp_earthquake2_uipreendofround`、`levels/sp_earthquake2/stagingarea_bigprops`、`levels/sp_earthquake2/stagingarea_sub`

**SP_Finale**（superbundle `levels/sp_finale/sp_finale`，22 个 bundle）

`levels/sp_finale/chase_sub`、`levels/sp_finale/credits`、`levels/sp_finale/escape_sub`、`levels/sp_finale/fight_sub`、`levels/sp_finale/level`、`levels/sp_finale/lightmap_01`、`levels/sp_finale/lightmap_02`、`levels/sp_finale/lightmap_03`、`levels/sp_finale/lightmap_04`、`levels/sp_finale/penn_sub`、`levels/sp_finale/sewerart_sub`、`levels/sp_finale/sp_finale`、`levels/sp_finale/sp_finale_gameconfiglight_win32`、`levels/sp_finale/sp_finale_loading_music`、`levels/sp_finale/sp_finale_settings_win32`、`levels/sp_finale/sp_finale_uiendofround`、`levels/sp_finale/sp_finale_uiloadingmp`、`levels/sp_finale/sp_finale_uiloadingsp`、`levels/sp_finale/sp_finale_uiplaying`、`levels/sp_finale/sp_finale_uipreendofround`、`levels/sp_finale/street_sub`、`levels/sp_finale/trainride_sub`

**SP_Jet**（superbundle `levels/sp_jet/sp_jet`，21 个 bundle）

`levels/sp_jet/area_carrierlanding`、`levels/sp_jet/area_dogfight_1`、`levels/sp_jet/area_dogfight_2`、`levels/sp_jet/area_fleet`、`levels/sp_jet/area_going_home`、`levels/sp_jet/area_highway_of_death`、`levels/sp_jet/art_dogfightparttwo_backdrop`、`levels/sp_jet/carrier_details`、`levels/sp_jet/carrier_interior`、`levels/sp_jet/carrierstart_playerandwingmananimations`、`levels/sp_jet/dogfightpartone_backdrop`、`levels/sp_jet/particleclouds`、`levels/sp_jet/sp_jet`、`levels/sp_jet/sp_jet_gameconfiglight_win32`、`levels/sp_jet/sp_jet_loading_music`、`levels/sp_jet/sp_jet_settings_win32`、`levels/sp_jet/sp_jet_uiendofround`、`levels/sp_jet/sp_jet_uiloadingmp`、`levels/sp_jet/sp_jet_uiloadingsp`、`levels/sp_jet/sp_jet_uiplaying`、`levels/sp_jet/sp_jet_uipreendofround`

**SP_New_York**（superbundle `levels/sp_new_york/sp_new_york`，12 个 bundle）

`levels/sp_new_york/level`、`levels/sp_new_york/lightmap_01`、`levels/sp_new_york/lightmap_02`、`levels/sp_new_york/sp_new_york`、`levels/sp_new_york/sp_new_york_gameconfiglight_win32`、`levels/sp_new_york/sp_new_york_settings_win32`、`levels/sp_new_york/sp_new_york_uiendofround`、`levels/sp_new_york/sp_new_york_uiloadingmp`、`levels/sp_new_york/sp_new_york_uiloadingsp`、`levels/sp_new_york/sp_new_york_uiplaying`、`levels/sp_new_york/sp_new_york_uipreendofround`、`levels/sp_new_york/trainride_sub`

**SP_Paris**（superbundle `levels/sp_paris/sp_paris`，33 个 bundle）

`levels/sp_paris/backdropbuildingsclose`、`levels/sp_paris/backdropbuildingsfar`、`levels/sp_paris/chase`、`levels/sp_paris/chaseintro`、`levels/sp_paris/corridorcorner`、`levels/sp_paris/corridorsluice`、`levels/sp_paris/gaseventsluice`、`levels/sp_paris/heat`、`levels/sp_paris/heat_pc_only`、`levels/sp_paris/lightmap_01`、`levels/sp_paris/lightmap_02`、`levels/sp_paris/lightmap_03`、`levels/sp_paris/lobby`、`levels/sp_paris/loweroffice`、`levels/sp_paris/loweroffice_pc`、`levels/sp_paris/parkingdeck`、`levels/sp_paris/parkingdeckgate`、`levels/sp_paris/parkingdeckgate_pc`、`levels/sp_paris/rail`、`levels/sp_paris/railbackdrop`、`levels/sp_paris/sp_paris`、`levels/sp_paris/sp_paris_gameconfiglight_win32`、`levels/sp_paris/sp_paris_loading_music`、`levels/sp_paris/sp_paris_settings_win32`、`levels/sp_paris/sp_paris_uiendofround`、`levels/sp_paris/sp_paris_uiloadingmp`、`levels/sp_paris/sp_paris_uiloadingsp`、`levels/sp_paris/sp_paris_uiplaying`、`levels/sp_paris/sp_paris_uipreendofround`、`levels/sp_paris/street`、`levels/sp_paris/tradingfloor`、`levels/sp_paris/upperoffice`、`levels/sp_paris/upperoffice_pc`

**SP_Sniper**（superbundle `levels/sp_sniper/sp_sniper`，37 个 bundle）

`levels/sp_sniper/albashirstrike`、`levels/sp_sniper/albashirstrikeart`、`levels/sp_sniper/albashirstrikeart_pc`、`levels/sp_sniper/background_01`、`levels/sp_sniper/background_02`、`levels/sp_sniper/background_persistant`、`levels/sp_sniper/backstreets`、`levels/sp_sniper/briefing`、`levels/sp_sniper/failknife`、`levels/sp_sniper/mall`、`levels/sp_sniper/mall_behindstreet`、`levels/sp_sniper/mall_exterior`、`levels/sp_sniper/mall_exterior_pc`、`levels/sp_sniper/mall_pc`、`levels/sp_sniper/malldefence`、`levels/sp_sniper/malldefence_animation1`、`levels/sp_sniper/malldefence_animation2`、`levels/sp_sniper/malldefence_animation3`、`levels/sp_sniper/malldefence_animation4`、`levels/sp_sniper/malldefence_animation5`、`levels/sp_sniper/mannequinroom`、`levels/sp_sniper/missile`、`levels/sp_sniper/overwatch`、`levels/sp_sniper/plaza`、`levels/sp_sniper/reconnest`、`levels/sp_sniper/reconnest_pc`、`levels/sp_sniper/rocketapartment`、`levels/sp_sniper/sewers`、`levels/sp_sniper/sp_sniper`、`levels/sp_sniper/sp_sniper_gameconfiglight_win32`、`levels/sp_sniper/sp_sniper_loading_music`、`levels/sp_sniper/sp_sniper_settings_win32`、`levels/sp_sniper/sp_sniper_uiendofround`、`levels/sp_sniper/sp_sniper_uiloadingmp`、`levels/sp_sniper/sp_sniper_uiloadingsp`、`levels/sp_sniper/sp_sniper_uiplaying`、`levels/sp_sniper/sp_sniper_uipreendofround`

**SP_Tank**（superbundle `levels/sp_tank/sp_tank`，33 个 bundle）

`levels/sp_tank/backdrop`、`levels/sp_tank/bankplaza_01`、`levels/sp_tank/desertfort`、`levels/sp_tank/desertfortpconly`、`levels/sp_tank/desertfortsmallobjects_01_levelart`、`levels/sp_tank/desertintro`、`levels/sp_tank/drivetobank_01_substream_01`、`levels/sp_tank/drivetobank_01_substream_02`、`levels/sp_tank/drivetobank_01_substream_03`、`levels/sp_tank/drivetobank_02_substream_01`、`levels/sp_tank/drivetobank_02_substream_02`、`levels/sp_tank/drivetobankplaza_01`、`levels/sp_tank/drivetobankplaza_02`、`levels/sp_tank/drivetobankplaza_03`、`levels/sp_tank/highwayofdeath`、`levels/sp_tank/highwayofdeath2`、`levels/sp_tank/highwayoverpass_01`、`levels/sp_tank/highwayoverpass_01_levelart_substream_01`、`levels/sp_tank/highwaytoteheran_01`、`levels/sp_tank/highwaytoteheran_02`、`levels/sp_tank/miclic`、`levels/sp_tank/miclic-highwaytoteheran`、`levels/sp_tank/miclicart`、`levels/sp_tank/roadtodesert_01`、`levels/sp_tank/sp_tank`、`levels/sp_tank/sp_tank_gameconfiglight_win32`、`levels/sp_tank/sp_tank_loading_music`、`levels/sp_tank/sp_tank_settings_win32`、`levels/sp_tank/sp_tank_uiendofround`、`levels/sp_tank/sp_tank_uiloadingmp`、`levels/sp_tank/sp_tank_uiloadingsp`、`levels/sp_tank/sp_tank_uiplaying`、`levels/sp_tank/sp_tank_uipreendofround`

**SP_Tank_b**（superbundle `levels/sp_tank_b/sp_tank_b`，23 个 bundle）

`levels/sp_tank_b/ambush`、`levels/sp_tank_b/bankplaza_01`、`levels/sp_tank_b/bankplazabackdrop`、`levels/sp_tank_b/blockedstreet`、`levels/sp_tank_b/blockedstreet2`、`levels/sp_tank_b/drivethrough`、`levels/sp_tank_b/drivetobankplaza_01`、`levels/sp_tank_b/drivetobankplaza_03`、`levels/sp_tank_b/introrail`、`levels/sp_tank_b/lightmap_01`、`levels/sp_tank_b/lightmap_02`、`levels/sp_tank_b/lightmap_03`、`levels/sp_tank_b/outroscene`、`levels/sp_tank_b/sidestreet`、`levels/sp_tank_b/sp_tank_b`、`levels/sp_tank_b/sp_tank_b_gameconfiglight_win32`、`levels/sp_tank_b/sp_tank_b_loading_music`、`levels/sp_tank_b/sp_tank_b_settings_win32`、`levels/sp_tank_b/sp_tank_b_uiendofround`、`levels/sp_tank_b/sp_tank_b_uiloadingmp`、`levels/sp_tank_b/sp_tank_b_uiloadingsp`、`levels/sp_tank_b/sp_tank_b_uiplaying`、`levels/sp_tank_b/sp_tank_b_uipreendofround`

**SP_Valley**（superbundle `levels/sp_valley/sp_valley`，33 个 bundle）

`levels/sp_valley/airdrop`、`levels/sp_valley/ambientwar`、`levels/sp_valley/briefingonhill`、`levels/sp_valley/forest`、`levels/sp_valley/forestart`、`levels/sp_valley/hillside`、`levels/sp_valley/ridge`、`levels/sp_valley/rundownhill`、`levels/sp_valley/sp_valley`、`levels/sp_valley/sp_valley_gameconfiglight_win32`、`levels/sp_valley/sp_valley_loading_music`、`levels/sp_valley/sp_valley_settings_win32`、`levels/sp_valley/sp_valley_uiendofround`、`levels/sp_valley/sp_valley_uiloadingmp`、`levels/sp_valley/sp_valley_uiloadingsp`、`levels/sp_valley/sp_valley_uiplaying`、`levels/sp_valley/sp_valley_uipreendofround`、`levels/sp_valley/valley`、`levels/sp_valley/valleyadvancetobridge`、`levels/sp_valley/valleyart`、`levels/sp_valley/valleyartillerycamp`、`levels/sp_valley/valleyfield1`、`levels/sp_valley/valleyfield2`、`levels/sp_valley/valleyjet`、`levels/sp_valley/valleyjet_endscene`、`levels/sp_valley/valleyjetbriefing`、`levels/sp_valley/valleytankbattle`、`levels/sp_valley/valleytankbriefing`、`levels/sp_valley/zone1`、`levels/sp_valley/zone2`、`levels/sp_valley/zone3`、`levels/sp_valley/zone4`、`levels/sp_valley/zone5`

**SP_Villa**（superbundle `levels/sp_villa/sp_villa`，34 个 bundle）

`levels/sp_villa/background`、`levels/sp_villa/basement`、`levels/sp_villa/blackburn`、`levels/sp_villa/chopper`、`levels/sp_villa/drive`、`levels/sp_villa/drive_2`、`levels/sp_villa/drive_pc`、`levels/sp_villa/garden`、`levels/sp_villa/garden_pc`、`levels/sp_villa/gatehouse`、`levels/sp_villa/halo`、`levels/sp_villa/halo_backdrop`、`levels/sp_villa/landing`、`levels/sp_villa/lightmap_01`、`levels/sp_villa/lightmap_02`、`levels/sp_villa/lightmap_03`、`levels/sp_villa/lightmap_cutscene01`、`levels/sp_villa/lightmap_cutscene02`、`levels/sp_villa/poolhouse`、`levels/sp_villa/poolhouse_extra`、`levels/sp_villa/rail`、`levels/sp_villa/railsuv`、`levels/sp_villa/sp_villa`、`levels/sp_villa/sp_villa_gameconfiglight_win32`、`levels/sp_villa/sp_villa_loading_music`、`levels/sp_villa/sp_villa_settings_win32`、`levels/sp_villa/sp_villa_uiendofround`、`levels/sp_villa/sp_villa_uiloadingmp`、`levels/sp_villa/sp_villa_uiloadingsp`、`levels/sp_villa/sp_villa_uiplaying`、`levels/sp_villa/sp_villa_uipreendofround`、`levels/sp_villa/villa`、`levels/sp_villa/villa_extra`、`levels/sp_villa/villa_pc`

**Web_Loading**（superbundle `levels/web_loading/web_loading`，8 个 bundle）

`levels/web_loading/web_loading`、`levels/web_loading/web_loading_gameconfiglight_win32`、`levels/web_loading/web_loading_settings_win32`、`levels/web_loading/web_loading_uiendofround`、`levels/web_loading/web_loading_uiloadingmp`、`levels/web_loading/web_loading_uiloadingsp`、`levels/web_loading/web_loading_uiplaying`、`levels/web_loading/web_loading_uipreendofround`

**XP1_001**（superbundle `levels/xp1_001/xp1_001`，16 个 bundle）

`levels/xp1_001/conquest_large`、`levels/xp1_001/conquest_small`、`levels/xp1_001/cq_s1`、`levels/xp1_001/rush`、`levels/xp1_001/squaddeathmatch`、`levels/xp1_001/squadrush`、`levels/xp1_001/tdm`、`levels/xp1_001/xp1_001`、`levels/xp1_001/xp1_001_gameconfiglight_win32`、`levels/xp1_001/xp1_001_loading_music`、`levels/xp1_001/xp1_001_settings_win32`、`levels/xp1_001/xp1_001_uiendofround`、`levels/xp1_001/xp1_001_uiloadingmp`、`levels/xp1_001/xp1_001_uiloadingsp`、`levels/xp1_001/xp1_001_uiplaying`、`levels/xp1_001/xp1_001_uipreendofround`

**XP1_002**（superbundle `levels/xp1_002/xp1_002`，16 个 bundle）

`levels/xp1_002/cq_l`、`levels/xp1_002/cq_s`、`levels/xp1_002/cq_s1`、`levels/xp1_002/r`、`levels/xp1_002/sqdm`、`levels/xp1_002/sr`、`levels/xp1_002/tdm`、`levels/xp1_002/xp1_002`、`levels/xp1_002/xp1_002_gameconfiglight_win32`、`levels/xp1_002/xp1_002_loading_music`、`levels/xp1_002/xp1_002_settings_win32`、`levels/xp1_002/xp1_002_uiendofround`、`levels/xp1_002/xp1_002_uiloadingmp`、`levels/xp1_002/xp1_002_uiloadingsp`、`levels/xp1_002/xp1_002_uiplaying`、`levels/xp1_002/xp1_002_uipreendofround`

**XP1_003**（superbundle `levels/xp1_003/xp1_003`，16 个 bundle）

`levels/xp1_003/cq_l`、`levels/xp1_003/cq_s`、`levels/xp1_003/cq_s1`、`levels/xp1_003/r`、`levels/xp1_003/sqdm`、`levels/xp1_003/sr`、`levels/xp1_003/tdm`、`levels/xp1_003/xp1_003`、`levels/xp1_003/xp1_003_gameconfiglight_win32`、`levels/xp1_003/xp1_003_loading_music`、`levels/xp1_003/xp1_003_settings_win32`、`levels/xp1_003/xp1_003_uiendofround`、`levels/xp1_003/xp1_003_uiloadingmp`、`levels/xp1_003/xp1_003_uiloadingsp`、`levels/xp1_003/xp1_003_uiplaying`、`levels/xp1_003/xp1_003_uipreendofround`

**XP1_004**（superbundle `levels/xp1_004/xp1_004`，15 个 bundle）

`levels/xp1_004/cq_l`、`levels/xp1_004/cq_s`、`levels/xp1_004/r`、`levels/xp1_004/sqdm`、`levels/xp1_004/sr`、`levels/xp1_004/tdm`、`levels/xp1_004/xp1_004`、`levels/xp1_004/xp1_004_gameconfiglight_win32`、`levels/xp1_004/xp1_004_loading_music`、`levels/xp1_004/xp1_004_settings_win32`、`levels/xp1_004/xp1_004_uiendofround`、`levels/xp1_004/xp1_004_uiloadingmp`、`levels/xp1_004/xp1_004_uiloadingsp`、`levels/xp1_004/xp1_004_uiplaying`、`levels/xp1_004/xp1_004_uipreendofround`

**XP2_Factory**（superbundle `levels/xp2_factory/xp2_factory`，14 个 bundle）

`levels/xp2_factory/deathmatch`、`levels/xp2_factory/dom2`、`levels/xp2_factory/gunmaster`、`levels/xp2_factory/sqdm`、`levels/xp2_factory/tdm`、`levels/xp2_factory/xp2_factory`、`levels/xp2_factory/xp2_factory_gameconfiglight_win32`、`levels/xp2_factory/xp2_factory_loading_music`、`levels/xp2_factory/xp2_factory_settings_win32`、`levels/xp2_factory/xp2_factory_uiendofround`、`levels/xp2_factory/xp2_factory_uiloadingmp`、`levels/xp2_factory/xp2_factory_uiloadingsp`、`levels/xp2_factory/xp2_factory_uiplaying`、`levels/xp2_factory/xp2_factory_uipreendofround`

**XP2_Office**（superbundle `levels/xp2_office/xp2_office`，14 个 bundle）

`levels/xp2_office/deathmatch`、`levels/xp2_office/domination`、`levels/xp2_office/gunmaster`、`levels/xp2_office/sqdm`、`levels/xp2_office/teamdeathmatch`、`levels/xp2_office/xp2_office`、`levels/xp2_office/xp2_office_gameconfiglight_win32`、`levels/xp2_office/xp2_office_loading_music`、`levels/xp2_office/xp2_office_settings_win32`、`levels/xp2_office/xp2_office_uiendofround`、`levels/xp2_office/xp2_office_uiloadingmp`、`levels/xp2_office/xp2_office_uiloadingsp`、`levels/xp2_office/xp2_office_uiplaying`、`levels/xp2_office/xp2_office_uipreendofround`

**XP2_Palace**（superbundle `levels/xp2_palace/xp2_palace`，14 个 bundle）

`levels/xp2_palace/deathmatch`、`levels/xp2_palace/domination`、`levels/xp2_palace/gunmaster`、`levels/xp2_palace/squaddeathmatch`、`levels/xp2_palace/teamdeathmatch`、`levels/xp2_palace/xp2_palace`、`levels/xp2_palace/xp2_palace_gameconfiglight_win32`、`levels/xp2_palace/xp2_palace_loading_music`、`levels/xp2_palace/xp2_palace_settings_win32`、`levels/xp2_palace/xp2_palace_uiendofround`、`levels/xp2_palace/xp2_palace_uiloadingmp`、`levels/xp2_palace/xp2_palace_uiloadingsp`、`levels/xp2_palace/xp2_palace_uiplaying`、`levels/xp2_palace/xp2_palace_uipreendofround`

**XP2_Skybar**（superbundle `levels/xp2_skybar/xp2_skybar`，14 个 bundle）

`levels/xp2_skybar/deathmatch`、`levels/xp2_skybar/domination`、`levels/xp2_skybar/gunmaster`、`levels/xp2_skybar/squaddm`、`levels/xp2_skybar/teamdm`、`levels/xp2_skybar/xp2_skybar`、`levels/xp2_skybar/xp2_skybar_gameconfiglight_win32`、`levels/xp2_skybar/xp2_skybar_loading_music`、`levels/xp2_skybar/xp2_skybar_settings_win32`、`levels/xp2_skybar/xp2_skybar_uiendofround`、`levels/xp2_skybar/xp2_skybar_uiloadingmp`、`levels/xp2_skybar/xp2_skybar_uiloadingsp`、`levels/xp2_skybar/xp2_skybar_uiplaying`、`levels/xp2_skybar/xp2_skybar_uipreendofround`

**XP3_Alborz**（superbundle `levels/xp3_alborz/xp3_alborz`，19 个 bundle）

`levels/xp3_alborz/conquest`、`levels/xp3_alborz/conquestlarge01`、`levels/xp3_alborz/conquestsmall01`、`levels/xp3_alborz/deathmatch`、`levels/xp3_alborz/rush`、`levels/xp3_alborz/rushlarge0`、`levels/xp3_alborz/sqdm`、`levels/xp3_alborz/squadrush0`、`levels/xp3_alborz/tanksuperiority`、`levels/xp3_alborz/tdm`、`levels/xp3_alborz/xp3_alborz`、`levels/xp3_alborz/xp3_alborz_gameconfiglight_win32`、`levels/xp3_alborz/xp3_alborz_loading_music`、`levels/xp3_alborz/xp3_alborz_settings_win32`、`levels/xp3_alborz/xp3_alborz_uiendofround`、`levels/xp3_alborz/xp3_alborz_uiloadingmp`、`levels/xp3_alborz/xp3_alborz_uiloadingsp`、`levels/xp3_alborz/xp3_alborz_uiplaying`、`levels/xp3_alborz/xp3_alborz_uipreendofround`

**XP3_Desert**（superbundle `levels/xp3_desert/xp3_desert`，19 个 bundle）

`levels/xp3_desert/conquest`、`levels/xp3_desert/conquestlarge0`、`levels/xp3_desert/conquestsmall0`、`levels/xp3_desert/deathmatch`、`levels/xp3_desert/rush`、`levels/xp3_desert/rushlarge0`、`levels/xp3_desert/squaddeathmatch1`、`levels/xp3_desert/squadrush0`、`levels/xp3_desert/tanksuperiority`、`levels/xp3_desert/teamdeathmatch1`、`levels/xp3_desert/xp3_desert`、`levels/xp3_desert/xp3_desert_gameconfiglight_win32`、`levels/xp3_desert/xp3_desert_loading_music`、`levels/xp3_desert/xp3_desert_settings_win32`、`levels/xp3_desert/xp3_desert_uiendofround`、`levels/xp3_desert/xp3_desert_uiloadingmp`、`levels/xp3_desert/xp3_desert_uiloadingsp`、`levels/xp3_desert/xp3_desert_uiplaying`、`levels/xp3_desert/xp3_desert_uipreendofround`

**XP3_Shield**（superbundle `levels/xp3_shield/xp3_shield`，19 个 bundle）

`levels/xp3_shield/conquest`、`levels/xp3_shield/conquestlarge0`、`levels/xp3_shield/conquestsmall0`、`levels/xp3_shield/deathmatch`、`levels/xp3_shield/rush`、`levels/xp3_shield/rushlarge`、`levels/xp3_shield/sqdm`、`levels/xp3_shield/squadrush`、`levels/xp3_shield/tanksuperiority`、`levels/xp3_shield/tdm`、`levels/xp3_shield/xp3_shield`、`levels/xp3_shield/xp3_shield_gameconfiglight_win32`、`levels/xp3_shield/xp3_shield_loading_music`、`levels/xp3_shield/xp3_shield_settings_win32`、`levels/xp3_shield/xp3_shield_uiendofround`、`levels/xp3_shield/xp3_shield_uiloadingmp`、`levels/xp3_shield/xp3_shield_uiloadingsp`、`levels/xp3_shield/xp3_shield_uiplaying`、`levels/xp3_shield/xp3_shield_uipreendofround`

**XP3_Valley**（superbundle `levels/xp3_valley/xp3_valley`，18 个 bundle）

`levels/xp3_valley/conquest`、`levels/xp3_valley/cql0`、`levels/xp3_valley/cqs0`、`levels/xp3_valley/deathmatch`、`levels/xp3_valley/rush`、`levels/xp3_valley/sqdm`、`levels/xp3_valley/squadrush`、`levels/xp3_valley/tanksuperiority`、`levels/xp3_valley/tdm`、`levels/xp3_valley/xp3_valley`、`levels/xp3_valley/xp3_valley_gameconfiglight_win32`、`levels/xp3_valley/xp3_valley_loading_music`、`levels/xp3_valley/xp3_valley_settings_win32`、`levels/xp3_valley/xp3_valley_uiendofround`、`levels/xp3_valley/xp3_valley_uiloadingmp`、`levels/xp3_valley/xp3_valley_uiloadingsp`、`levels/xp3_valley/xp3_valley_uiplaying`、`levels/xp3_valley/xp3_valley_uipreendofround`

**XP4_FD**（superbundle `levels/xp4_fd/xp4_fd`，20 个 bundle）

`levels/xp4_fd/conquest`、`levels/xp4_fd/conquest_large`、`levels/xp4_fd/conquest_small0`、`levels/xp4_fd/deathmatch`、`levels/xp4_fd/gunmaster`、`levels/xp4_fd/rush`、`levels/xp4_fd/rushes`、`levels/xp4_fd/scavenger_v2`、`levels/xp4_fd/squaddeathmatch`、`levels/xp4_fd/squadrush`、`levels/xp4_fd/teamdeathmatch`、`levels/xp4_fd/xp4_fd`、`levels/xp4_fd/xp4_fd_gameconfiglight_win32`、`levels/xp4_fd/xp4_fd_loading_music`、`levels/xp4_fd/xp4_fd_settings_win32`、`levels/xp4_fd/xp4_fd_uiendofround`、`levels/xp4_fd/xp4_fd_uiloadingmp`、`levels/xp4_fd/xp4_fd_uiloadingsp`、`levels/xp4_fd/xp4_fd_uiplaying`、`levels/xp4_fd/xp4_fd_uipreendofround`

**XP4_Parl**（superbundle `levels/xp4_parl/xp4_parl`，20 个 bundle）

`levels/xp4_parl/conquest`、`levels/xp4_parl/conquest_large`、`levels/xp4_parl/conquest_small`、`levels/xp4_parl/deathmatch`、`levels/xp4_parl/gunmaster`、`levels/xp4_parl/rush`、`levels/xp4_parl/rushlarge`、`levels/xp4_parl/scavenger`、`levels/xp4_parl/squaddeathmatch`、`levels/xp4_parl/squadrush`、`levels/xp4_parl/teamdeathmatch`、`levels/xp4_parl/xp4_parl`、`levels/xp4_parl/xp4_parl_gameconfiglight_win32`、`levels/xp4_parl/xp4_parl_loading_music`、`levels/xp4_parl/xp4_parl_settings_win32`、`levels/xp4_parl/xp4_parl_uiendofround`、`levels/xp4_parl/xp4_parl_uiloadingmp`、`levels/xp4_parl/xp4_parl_uiloadingsp`、`levels/xp4_parl/xp4_parl_uiplaying`、`levels/xp4_parl/xp4_parl_uipreendofround`

**XP4_Quake**（superbundle `levels/xp4_quake/xp4_quake`，20 个 bundle）

`levels/xp4_quake/conquest`、`levels/xp4_quake/conquest_large`、`levels/xp4_quake/conquest_small`、`levels/xp4_quake/deathmatch`、`levels/xp4_quake/gunmaster`、`levels/xp4_quake/rushes`、`levels/xp4_quake/rushlarge`、`levels/xp4_quake/scavenger`、`levels/xp4_quake/squaddeathmatch`、`levels/xp4_quake/squadrush`、`levels/xp4_quake/teamdeathmatch`、`levels/xp4_quake/xp4_quake`、`levels/xp4_quake/xp4_quake_gameconfiglight_win32`、`levels/xp4_quake/xp4_quake_loading_music`、`levels/xp4_quake/xp4_quake_settings_win32`、`levels/xp4_quake/xp4_quake_uiendofround`、`levels/xp4_quake/xp4_quake_uiloadingmp`、`levels/xp4_quake/xp4_quake_uiloadingsp`、`levels/xp4_quake/xp4_quake_uiplaying`、`levels/xp4_quake/xp4_quake_uipreendofround`

**XP4_Rubble**（superbundle `levels/xp4_rubble/xp4_rubble`，20 个 bundle）

`levels/xp4_rubble/conquest`、`levels/xp4_rubble/conquest_large`、`levels/xp4_rubble/conquest_small`、`levels/xp4_rubble/deatmatch`、`levels/xp4_rubble/gunmaster`、`levels/xp4_rubble/rush_large`、`levels/xp4_rubble/rushes`、`levels/xp4_rubble/scavenger`、`levels/xp4_rubble/squad_rush`、`levels/xp4_rubble/squaddeathmatch`、`levels/xp4_rubble/teamdeathmatch`、`levels/xp4_rubble/xp4_rubble`、`levels/xp4_rubble/xp4_rubble_gameconfiglight_win32`、`levels/xp4_rubble/xp4_rubble_loading_music`、`levels/xp4_rubble/xp4_rubble_settings_win32`、`levels/xp4_rubble/xp4_rubble_uiendofround`、`levels/xp4_rubble/xp4_rubble_uiloadingmp`、`levels/xp4_rubble/xp4_rubble_uiloadingsp`、`levels/xp4_rubble/xp4_rubble_uiplaying`、`levels/xp4_rubble/xp4_rubble_uipreendofround`

**XP5_001**（superbundle `levels/xp5_001/xp5_001`，19 个 bundle）

`levels/xp5_001/air_superiority`、`levels/xp5_001/conquest`、`levels/xp5_001/cql`、`levels/xp5_001/cqs`、`levels/xp5_001/ctf`、`levels/xp5_001/dm`、`levels/xp5_001/rush`、`levels/xp5_001/sqdm`、`levels/xp5_001/squadrush`、`levels/xp5_001/tdm`、`levels/xp5_001/xp5_001`、`levels/xp5_001/xp5_001_gameconfiglight_win32`、`levels/xp5_001/xp5_001_loading_music`、`levels/xp5_001/xp5_001_settings_win32`、`levels/xp5_001/xp5_001_uiendofround`、`levels/xp5_001/xp5_001_uiloadingmp`、`levels/xp5_001/xp5_001_uiloadingsp`、`levels/xp5_001/xp5_001_uiplaying`、`levels/xp5_001/xp5_001_uipreendofround`

**XP5_002**（superbundle `levels/xp5_002/xp5_002`，19 个 bundle）

`levels/xp5_002/air_superiority`、`levels/xp5_002/conquest`、`levels/xp5_002/cql`、`levels/xp5_002/cqs`、`levels/xp5_002/ctf`、`levels/xp5_002/dm`、`levels/xp5_002/rush`、`levels/xp5_002/sqdm`、`levels/xp5_002/squadrush`、`levels/xp5_002/tdm`、`levels/xp5_002/xp5_002`、`levels/xp5_002/xp5_002_gameconfiglight_win32`、`levels/xp5_002/xp5_002_loading_music`、`levels/xp5_002/xp5_002_settings_win32`、`levels/xp5_002/xp5_002_uiendofround`、`levels/xp5_002/xp5_002_uiloadingmp`、`levels/xp5_002/xp5_002_uiloadingsp`、`levels/xp5_002/xp5_002_uiplaying`、`levels/xp5_002/xp5_002_uipreendofround`

**XP5_003**（superbundle `levels/xp5_003/xp5_003`，19 个 bundle）

`levels/xp5_003/airsueriority`、`levels/xp5_003/conquest`、`levels/xp5_003/cql`、`levels/xp5_003/cqs`、`levels/xp5_003/ctf`、`levels/xp5_003/dm`、`levels/xp5_003/rush`、`levels/xp5_003/sqdm`、`levels/xp5_003/squadrush`、`levels/xp5_003/tdm`、`levels/xp5_003/xp5_003`、`levels/xp5_003/xp5_003_gameconfiglight_win32`、`levels/xp5_003/xp5_003_loading_music`、`levels/xp5_003/xp5_003_settings_win32`、`levels/xp5_003/xp5_003_uiendofround`、`levels/xp5_003/xp5_003_uiloadingmp`、`levels/xp5_003/xp5_003_uiloadingsp`、`levels/xp5_003/xp5_003_uiplaying`、`levels/xp5_003/xp5_003_uipreendofround`

**XP5_004**（superbundle `levels/xp5_004/xp5_004`，19 个 bundle）

`levels/xp5_004/airsuperiority`、`levels/xp5_004/conquest`、`levels/xp5_004/cql`、`levels/xp5_004/cqs`、`levels/xp5_004/ctf`、`levels/xp5_004/dm`、`levels/xp5_004/rush`、`levels/xp5_004/sqdm`、`levels/xp5_004/squadrush`、`levels/xp5_004/tdm`、`levels/xp5_004/xp5_004`、`levels/xp5_004/xp5_004_gameconfiglight_win32`、`levels/xp5_004/xp5_004_loading_music`、`levels/xp5_004/xp5_004_settings_win32`、`levels/xp5_004/xp5_004_uiendofround`、`levels/xp5_004/xp5_004_uiloadingmp`、`levels/xp5_004/xp5_004_uiloadingsp`、`levels/xp5_004/xp5_004_uiplaying`、`levels/xp5_004/xp5_004_uipreendofround`

> 覆盖 997 个 bundle；全量表见 VU 官方文档 bundles 页（本工具索引目录缓存一份于 ~/.bundles-guid/bundles.md）。

## 资料与出处（技能桥）

| 本表内容 | 出处（本地技能库镜像 = VU 官方文档同名页） |
|---|---|
| MountSuperBundle / LoadBundles / compartment 官方语义 | `references\vext\guides\custom-content.md` |
| compartment 枚举全表 | `references\vext\ref\shared\type\resourcecompartment.md` |
| AddRegistry 签名 (registry, compartment) | `references\vext\ref\shared\library\resourcemanager.md` |
| 生命周期三时机与注入时机 | `lua-patterns.md` §13 |
| 检索纪律（GUID→文件头、禁止按名猜） | `ebx-retrieval.md` §2 / §C.1 |
| AddRegistry 实战（133F6403 注入链） | 案例 04 / venice-ebx-structure §4 |
| 数据口径与特例 | 本目录 FINDINGS.md |

---
注册表合计 608 个，覆盖 49 张图。
